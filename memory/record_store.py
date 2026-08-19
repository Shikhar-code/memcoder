"""Local SQLite source of truth for guidance records.

The vector database is a retrieval index, not the authority for record identity,
provenance, or lifecycle state.  SQLite is in the standard library, so this
layer remains local-first and provider-independent.
"""

import json
import os
import re
import sqlite3
from contextlib import closing, contextmanager
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
RECORD_STORE_SCHEMA_VERSION = 3
SCHEMA_VERSION_KEY = "record_store_schema_version"
LEXICAL_INDEX_NAME = "guidance_records_fts"


def _database_path():
    configured = os.environ.get("MEMCODER_RECORD_DB_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import active_db_path
    return Path(active_db_path()).parent / "memcoder_records.sqlite3"


@contextmanager
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
    _ensure_lexical_index(connection)
    connection.execute(
        "INSERT OR REPLACE INTO record_store_metadata(key, value) VALUES (?, ?)",
        (SCHEMA_VERSION_KEY, str(RECORD_STORE_SCHEMA_VERSION)),
    )
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _ensure_lexical_index(connection):
    """Create the rebuildable FTS5 sidecar when this Python supports it."""
    try:
        connection.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {LEXICAL_INDEX_NAME}
            USING fts5(record_id UNINDEXED, owner UNINDEXED, record_type UNINDEXED, document)
        """)
        connection.execute(f"""
            INSERT INTO {LEXICAL_INDEX_NAME}(record_id, owner, record_type, document)
            SELECT records.record_id, records.owner, records.record_type, records.document
            FROM guidance_records AS records
            WHERE NOT EXISTS (
                SELECT 1 FROM {LEXICAL_INDEX_NAME} AS search
                WHERE search.record_id = records.record_id
            )
        """)
        return True
    except sqlite3.OperationalError:
        # FTS5 is optional in SQLite builds. The bounded LIKE fallback below
        # preserves retrieval without adding a dependency.
        return False


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
        try:
            connection.execute(
                f"DELETE FROM {LEXICAL_INDEX_NAME} WHERE record_id = ?",
                (record_id(memory),),
            )
            connection.execute(
                f"INSERT INTO {LEXICAL_INDEX_NAME}(record_id, owner, record_type, document) "
                "VALUES (?, ?, ?, ?)",
                (record_id(memory), memory["owner"], memory["type"], document),
            )
        except sqlite3.OperationalError:
            pass
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
        try:
            connection.execute(
                f"DELETE FROM {LEXICAL_INDEX_NAME} WHERE record_id IN ({placeholders})", ids
            )
        except sqlite3.OperationalError:
            pass
        cursor = connection.execute(
            f"DELETE FROM guidance_records WHERE record_id IN ({placeholders})", ids
        )
    return cursor.rowcount


def delete_owner(owner):
    with _connect() as connection:
        try:
            connection.execute(
                f"DELETE FROM {LEXICAL_INDEX_NAME} WHERE owner = ?", (owner,)
            )
        except sqlite3.OperationalError:
            pass
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


def has_records():
    """Check the SQLite source of truth without creating a database or schema."""
    path = storage_path()
    if not path.exists():
        return False
    try:
        with closing(sqlite3.connect(path)) as connection:
            table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'guidance_records'"
            ).fetchone()
            return bool(table and connection.execute(
                "SELECT 1 FROM guidance_records LIMIT 1"
            ).fetchone())
    except sqlite3.Error:
        return False


def lexical_status():
    """Describe the local lexical fallback without loading semantic retrieval."""
    path = storage_path()
    if not path.exists():
        return {
            "available": True,
            "backend": "sqlite_like",
            "records": 0,
            "schema_version": RECORD_STORE_SCHEMA_VERSION,
        }
    try:
        with _connect() as connection:
            records = connection.execute("SELECT COUNT(*) FROM guidance_records").fetchone()[0]
            fts = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                (LEXICAL_INDEX_NAME,),
            ).fetchone()
        return {
            "available": True,
            "backend": "sqlite_fts5" if fts else "sqlite_like",
            "records": records,
            "schema_version": RECORD_STORE_SCHEMA_VERSION,
        }
    except sqlite3.Error as error:
        return {
            "available": False,
            "backend": "unavailable",
            "records": 0,
            "schema_version": RECORD_STORE_SCHEMA_VERSION,
            "error": str(error),
        }


def inspect_schema():
    """Inspect the durable schema without creating or upgrading it."""
    path = storage_path()
    if not path.exists():
        return {"path": str(path), "schema_version": 0, "records": 0, "exists": False}
    try:
        with closing(sqlite3.connect(path)) as connection:
            table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'guidance_records'"
            ).fetchone()
            records = connection.execute(
                "SELECT COUNT(*) FROM guidance_records"
            ).fetchone()[0] if table else 0
            metadata = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'record_store_metadata'"
            ).fetchone()
            version = 0
            if metadata:
                row = connection.execute(
                    "SELECT value FROM record_store_metadata WHERE key = ?", (SCHEMA_VERSION_KEY,)
                ).fetchone()
                version = int(row[0]) if row else 2
        return {"path": str(path), "schema_version": version, "records": records, "exists": True}
    except (sqlite3.Error, ValueError) as error:
        return {"path": str(path), "schema_version": None, "records": 0, "exists": True, "error": str(error)}


def ensure_schema():
    """Apply only additive, rebuildable schema changes and verify the result."""
    with _connect() as connection:
        records = connection.execute("SELECT COUNT(*) FROM guidance_records").fetchone()[0]
        version = connection.execute(
            "SELECT value FROM record_store_metadata WHERE key = ?", (SCHEMA_VERSION_KEY,)
        ).fetchone()[0]
    return {
        "path": str(storage_path()),
        "schema_version": int(version),
        "records": records,
        "lexical": lexical_status(),
    }


def _lexical_result(memory, query):
    from memory.proof import build_proof
    from memory.relevance import lexical_overlap

    result = dict(memory)
    result["id"] = record_id(result)
    overlap = lexical_overlap(result, query)
    confidence = min(0.92, 0.60 + min(overlap, 4) * 0.08)
    result["score"] = round(2.0 * (1.0 - confidence), 4)
    result["retrieval_backend"] = "lexical"
    result["proof"] = build_proof(result)
    return result


def search_records_lexical(query, owner="human", include_shared=True, record_type=None, limit=8):
    """Return bounded local candidates without importing Chroma or an embedder."""
    from memory.relevance import query_terms

    terms = sorted(query_terms(query))[:12]
    if not terms or not has_records():
        return []
    limit = max(1, min(50, int(limit)))
    owners = [owner, "shared"] if include_shared and owner != "shared" else [owner]
    placeholders = ", ".join("?" for _ in owners)
    filters = [f"records.owner IN ({placeholders})", "records.record_state = 'trusted'"]
    parameters = list(owners)
    if record_type:
        filters.append("records.record_type = ?")
        parameters.append(record_type)
    where = " AND ".join(filters)

    with _connect() as connection:
        fts = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (LEXICAL_INDEX_NAME,),
        ).fetchone()
        rows = []
        if fts:
            match = " OR ".join(f'"{term}"' for term in terms)
            try:
                rows = connection.execute(f"""
                    SELECT records.*
                    FROM {LEXICAL_INDEX_NAME} AS search
                    JOIN guidance_records AS records ON records.record_id = search.record_id
                    WHERE {LEXICAL_INDEX_NAME} MATCH ? AND {where}
                    ORDER BY bm25({LEXICAL_INDEX_NAME})
                    LIMIT ?
                """, [match, *parameters, limit]).fetchall()
            except sqlite3.OperationalError:
                rows = []
        if not rows:
            like = " OR ".join("LOWER(records.document) LIKE ?" for _ in terms)
            rows = connection.execute(f"""
                SELECT records.* FROM guidance_records AS records
                WHERE ({like}) AND {where}
                LIMIT ?
            """, [*(f"%{term}%" for term in terms), *parameters, limit]).fetchall()

    candidates = [_lexical_result(_decode(row), query) for row in rows]
    return sorted(
        candidates,
        key=lambda item: (-len(set(re.findall(r"[a-z0-9_]+", query.lower())) &
                               set(re.findall(r"[a-z0-9_]+", item.get("solution", "").lower()))),
                          item.get("updated_at", "")),
    )[:limit]


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
