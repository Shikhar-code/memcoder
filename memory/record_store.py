"""Local SQLite source of truth for guidance records.

The vector database is a retrieval index, not the authority for record identity,
provenance, or lifecycle state.  SQLite is in the standard library, so this
layer remains local-first and provider-independent.
"""

import json
import os
import sqlite3
from pathlib import Path

from memory.memory_hash import memory_hash
from memory.records import (
    GUIDANCE_RECORD_SCHEMA_VERSION,
    initialize_record,
    record_id,
    searchable_document,
)


MIGRATION_KEY = "legacy_chroma_migrated_v2"
LEGACY_WORKSPACE_MIGRATION_KEY = "legacy_workspace_migrated_v2"


def _database_path():
    configured = os.environ.get("MEMCODER_RECORD_DB_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_records.sqlite3"


def _connect():
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("""
        CREATE TABLE IF NOT EXISTS guidance_records (
            record_id TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL,
            owner TEXT NOT NULL,
            record_type TEXT NOT NULL,
            record_state TEXT NOT NULL,
            revision INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            document TEXT NOT NULL,
            metadata_json TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE INDEX IF NOT EXISTS guidance_records_duplicate_lookup
        ON guidance_records(content_hash, owner)
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS record_store_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS record_edges (
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relation TEXT NOT NULL,
            owner TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(source_id, target_id, relation, owner)
        )
    """)
    connection.execute("""
        CREATE INDEX IF NOT EXISTS record_edges_source_lookup
        ON record_edges(source_id, owner)
    """)
    connection.execute("""
        CREATE INDEX IF NOT EXISTS record_edges_target_lookup
        ON record_edges(target_id, owner)
    """)
    return connection


def _decode(row):
    memory = json.loads(row["metadata_json"])
    memory.setdefault("record_id", row["record_id"])
    memory.setdefault("content_hash", row["content_hash"])
    memory.setdefault("hash", row["content_hash"])
    memory.setdefault("record_state", row["record_state"])
    memory.setdefault("revision", row["revision"])
    memory.setdefault("created_at", row["created_at"])
    memory.setdefault("updated_at", row["updated_at"])
    return memory


def save_record(memory, document=None):
    """Insert or update one guidance record in the durable local store."""
    initialize_record(memory)
    document = document or searchable_document(memory)
    payload = json.dumps(memory, sort_keys=True, ensure_ascii=False)
    with _connect() as connection:
        cursor = connection.execute("""
            INSERT INTO guidance_records (
                record_id, content_hash, owner, record_type, record_state,
                revision, created_at, updated_at, document, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(record_id) DO UPDATE SET
                content_hash=excluded.content_hash,
                owner=excluded.owner,
                record_type=excluded.record_type,
                record_state=excluded.record_state,
                revision=excluded.revision,
                updated_at=excluded.updated_at,
                document=excluded.document,
                metadata_json=excluded.metadata_json
        """, (
            record_id(memory), memory["content_hash"], memory["owner"],
            memory["type"], memory["record_state"], memory["revision"],
            memory["created_at"], memory["updated_at"], document, payload,
        ))
    return memory


def get_record(memory_id):
    with _connect() as connection:
        row = connection.execute(
            "SELECT * FROM guidance_records WHERE record_id = ?", (memory_id,)
        ).fetchone()
    return _decode(row) if row else None


def find_duplicate(content_hash, owner):
    with _connect() as connection:
        row = connection.execute("""
            SELECT * FROM guidance_records
            WHERE content_hash = ? AND owner = ?
            ORDER BY created_at ASC LIMIT 1
        """, (content_hash, owner)).fetchone()
    return _decode(row) if row else None


def list_records():
    with _connect() as connection:
        rows = connection.execute(
            "SELECT * FROM guidance_records ORDER BY created_at ASC"
        ).fetchall()
    return [_decode(row) for row in rows]


def delete_records(ids):
    if not ids:
        return 0
    placeholders = ", ".join("?" for _ in ids)
    with _connect() as connection:
        cursor = connection.execute(
            f"DELETE FROM guidance_records WHERE record_id IN ({placeholders})", ids
        )
    return cursor.rowcount


def delete_owner(owner):
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM guidance_records WHERE owner = ?", (owner,)
        )
    return cursor.rowcount


def add_edge(source_id, target_id, relation, owner, metadata=None, created_at=None):
    """Store one typed, owner-scoped provenance edge without overwriting history."""
    from memory.provenance import VALID_EDGE_RELATIONS
    from memory.records import utc_now

    if relation not in VALID_EDGE_RELATIONS:
        raise ValueError(f"Unsupported provenance relation: {relation}")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("source_id must be a non-empty record ID.")
    if not isinstance(target_id, str) or not target_id.strip():
        raise ValueError("target_id must be a non-empty record or audit ID.")
    if source_id == target_id:
        raise ValueError("A provenance edge cannot point to the same record.")

    with _connect() as connection:
        source = connection.execute(
            "SELECT record_id FROM guidance_records WHERE record_id = ?", (source_id,)
        ).fetchone()
        if source is None:
            raise ValueError(f"Provenance source record was not found: {source_id}")
        cursor = connection.execute("""
            INSERT OR IGNORE INTO record_edges(
                source_id, target_id, relation, owner, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            source_id, target_id, relation, owner,
            json.dumps(metadata or {}, sort_keys=True, ensure_ascii=False),
            created_at or utc_now(),
        ))
    return cursor.rowcount


def edges_for(record_id_value, owner=None):
    """Return direct incoming and outgoing provenance edges for one record."""
    query = """
        SELECT source_id, target_id, relation, owner, metadata_json, created_at
        FROM record_edges WHERE source_id = ? OR target_id = ?
    """
    parameters = [record_id_value, record_id_value]
    if owner is not None:
        query += " AND owner = ?"
        parameters.append(owner)
    with _connect() as connection:
        rows = connection.execute(query, parameters).fetchall()
    edges = []
    for row in rows:
        edges.append({
            "source_id": row["source_id"],
            "target_id": row["target_id"],
            "relation": row["relation"],
            "owner": row["owner"],
            "metadata": json.loads(row["metadata_json"]),
            "created_at": row["created_at"],
            "direction": "outgoing" if row["source_id"] == record_id_value else "incoming",
        })
    return sorted(edges, key=lambda edge: edge["created_at"])


def list_edges():
    """Return every durable provenance edge for export and backup."""
    with _connect() as connection:
        rows = connection.execute("""
            SELECT source_id, target_id, relation, owner, metadata_json, created_at
            FROM record_edges ORDER BY created_at ASC
        """).fetchall()
    return [{
        "source_id": row["source_id"],
        "target_id": row["target_id"],
        "relation": row["relation"],
        "owner": row["owner"],
        "metadata": json.loads(row["metadata_json"]),
        "created_at": row["created_at"],
    } for row in rows]


def storage_path():
    """Expose the durable database path without making callers know internals."""
    return _database_path()


def _migration_completed(connection):
    row = connection.execute(
        "SELECT value FROM record_store_metadata WHERE key = ?", (MIGRATION_KEY,)
    ).fetchone()
    return row is not None


def migrate_legacy_chroma(collection, migration_key=MIGRATION_KEY):
    """Copy Chroma-only records into SQLite once, preserving legacy IDs."""
    with _connect() as connection:
        row = connection.execute(
            "SELECT value FROM record_store_metadata WHERE key = ?", (migration_key,)
        ).fetchone()
        if row is not None:
            return {"migrated": 0, "already_migrated": True}

    result = collection.get(include=["metadatas", "documents"])
    migrated = 0
    for legacy_id, metadata, document in zip(
            result.get("ids", []), result.get("metadatas", []), result.get("documents", [])):
        memory = dict(metadata or {})
        memory.setdefault("record_id", legacy_id)
        memory.setdefault("type", "experience")
        memory.setdefault("owner", "shared")
        memory.setdefault("files", ["unknown"])
        memory.setdefault("summary", "")
        memory.setdefault("solution", "Unknown")
        memory.setdefault("task", "")
        memory.setdefault("record_state", "trusted")
        memory.setdefault("revision", 1)
        memory.setdefault("schema_version", GUIDANCE_RECORD_SCHEMA_VERSION)
        memory.setdefault("created_at", memory.get("timestamp") or "legacy")
        memory.setdefault("updated_at", memory.get("timestamp") or "legacy")
        memory["content_hash"] = memory_hash(memory)
        memory["hash"] = memory["content_hash"]
        save_record(memory, document=document or searchable_document(memory))
        migrated += 1

    with _connect() as connection:
        connection.execute(
            "INSERT OR REPLACE INTO record_store_metadata(key, value) VALUES (?, ?)",
            (migration_key, "complete"),
        )
    return {"migrated": migrated, "already_migrated": False}


def migrate_legacy_workspace_storage():
    """Import pre-Beta-2.1 workspace data after defaults move to user storage."""
    with _connect() as connection:
        row = connection.execute(
            "SELECT value FROM record_store_metadata WHERE key = ?",
            (LEGACY_WORKSPACE_MIGRATION_KEY,),
        ).fetchone()
        if row is not None:
            return {"already_migrated": True, "records": 0, "edges": 0, "audits": 0}

    from memory.chroma_client import legacy_workspace_collection, legacy_workspace_db_path

    chroma_result = {"migrated": 0, "already_migrated": False}
    legacy_collection = legacy_workspace_collection()
    if legacy_collection is not None:
        chroma_result = migrate_legacy_chroma(
            legacy_collection,
            migration_key="legacy_workspace_chroma_migrated_v2",
        )

    records = edges = audits = 0
    legacy_store = legacy_workspace_db_path.parent / "memcoder_records.sqlite3"
    if legacy_store.exists() and legacy_store != storage_path():
        source = sqlite3.connect(legacy_store)
        source.row_factory = sqlite3.Row
        try:
            rows = source.execute("SELECT metadata_json FROM guidance_records").fetchall()
            for row in rows:
                memory = json.loads(row["metadata_json"])
                existing = get_record(memory.get("record_id", ""))
                if existing and int(existing.get("revision", 1)) >= int(memory.get("revision", 1)):
                    continue
                save_record(memory)
                records += 1
            edge_rows = source.execute("""
                SELECT source_id, target_id, relation, owner, metadata_json, created_at
                FROM record_edges
            """).fetchall()
            for row in edge_rows:
                try:
                    edges += add_edge(
                        row["source_id"], row["target_id"], row["relation"], row["owner"],
                        metadata=json.loads(row["metadata_json"]), created_at=row["created_at"],
                    )
                except ValueError:
                    continue
        except sqlite3.OperationalError:
            # A pre-release/partial store is still recoverable from Chroma.
            pass
        finally:
            source.close()

        legacy_audits = legacy_store.parent / "memcoder_plan_outcomes.jsonl"
        if legacy_audits.exists():
            from memory.audit_store import merge_audit_entries
            entries = []
            for line in legacy_audits.read_text(encoding="utf-8").splitlines():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            audits = merge_audit_entries(entries)

    with _connect() as connection:
        connection.execute(
            "INSERT OR REPLACE INTO record_store_metadata(key, value) VALUES (?, ?)",
            (LEGACY_WORKSPACE_MIGRATION_KEY, "complete"),
        )
    return {
        "already_migrated": False,
        "records": records + chroma_result["migrated"],
        "edges": edges,
        "audits": audits,
    }


def rebuild_guidance_index(collection, embed):
    """Recreate the semantic index entirely from durable SQLite records."""
    records = list_records()
    existing = collection.get()
    if existing.get("ids"):
        collection.delete(ids=existing["ids"])
    for memory in records:
        document = searchable_document(memory)
        collection.add(
            ids=[record_id(memory)],
            documents=[document],
            embeddings=[embed(document)],
            metadatas=[memory],
        )
    return {"indexed": len(records), "removed": len(existing.get("ids", []))}
