"""Portable, conservative operational controls for local MemCoder storage."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


SNAPSHOT_SCHEMA_VERSION = 1
SNAPSHOT_MEMBER = "memcoder_snapshot.json"


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def storage_status():
    from memory.audit_store import list_audit_entries
    from memory.record_store import inspect_schema, lexical_status, list_edges, list_records, storage_path

    records = list_records()
    from memory.dreaming import snapshot_candidates
    dream_candidates = snapshot_candidates()
    from memory.failure_frontier import list_frontiers
    from memory.cognitive_branch import list_branches
    by_state = {}
    by_type = {}
    for record in records:
        by_state[record.get("record_state", "trusted")] = by_state.get(
            record.get("record_state", "trusted"), 0
        ) + 1
        by_type[record.get("type", "unknown")] = by_type.get(
            record.get("type", "unknown"), 0
        ) + 1
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "record_database": str(storage_path()),
        "records": len(records),
        "records_by_state": by_state,
        "records_by_type": by_type,
        "provenance_edges": len(list_edges()),
        "plan_audits": len(list_audit_entries()),
        "dream_candidates": len(dream_candidates),
        "failure_frontiers": len(list_frontiers()),
        "cognitive_branches": len(list_branches()),
        "schema": inspect_schema(),
        "lexical": lexical_status(),
    }


def upgrade_storage(dry_run=False):
    """Upgrade the additive local schema with a byte-safe SQLite rollback copy."""
    from memory.record_store import RECORD_STORE_SCHEMA_VERSION, ensure_schema, inspect_schema, storage_path

    before = inspect_schema()
    plan = {
        "from_version": before.get("schema_version", 0),
        "to_version": RECORD_STORE_SCHEMA_VERSION,
        "records": before.get("records", 0),
        "changes": ["add or refresh the rebuildable SQLite FTS5 lexical index"],
        "authoritative_records_changed": False,
    }
    if dry_run:
        return {"dry_run": True, "plan": plan}

    path = storage_path()
    rollback = None
    if path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        rollback = path.parent / "backups" / f"records-before-v{RECORD_STORE_SCHEMA_VERSION}-{timestamp}.sqlite3"
        rollback.parent.mkdir(parents=True, exist_ok=True)
        source, target = sqlite3.connect(path), sqlite3.connect(rollback)
        try:
            source.backup(target)
        finally:
            source.close()
            target.close()
    try:
        after = ensure_schema()
        if after["schema_version"] != RECORD_STORE_SCHEMA_VERSION:
            raise RuntimeError("record store schema verification failed")
        if after["records"] != before.get("records", 0):
            raise RuntimeError("record count changed during additive schema upgrade")
    except Exception:
        if rollback is not None:
            source, target = sqlite3.connect(rollback), sqlite3.connect(path)
            try:
                source.backup(target)
            finally:
                source.close()
                target.close()
        raise
    return {
        "dry_run": False,
        "plan": plan,
        "backup": str(rollback) if rollback else None,
        "validated": True,
        "after": after,
    }


def build_snapshot():
    from memory.audit_store import list_audit_entries
    from memory.record_store import list_edges, list_records
    from memory.dreaming import snapshot_candidates
    from memory.failure_frontier import list_frontiers
    from memory.cognitive_branch import list_branches

    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "exported_at": _utc_now(),
        "records": list_records(),
        "provenance_edges": list_edges(),
        "plan_audits": list_audit_entries(),
        "dream_candidates": snapshot_candidates(),
        "failure_frontiers": list_frontiers(),
        "cognitive_branches": list_branches(),
    }


def export_snapshot(output_path=None):
    if output_path is None:
        from memory.record_store import storage_path
        output_path = storage_path().parent / "exports" / "memcoder-snapshot.json"
    path = Path(output_path)
    if path.suffix.lower() != ".json":
        raise ValueError("export path must end in .json")
    path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = build_snapshot()
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"path": str(path), "records": len(snapshot["records"])}


def create_backup(output_path=None):
    from memory.record_store import storage_path

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = storage_path().parent / "backups" / f"memcoder-{timestamp}.zip"
    path = Path(output_path)
    if path.suffix.lower() != ".zip":
        raise ValueError("backup path must end in .zip")
    path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = build_snapshot()
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(SNAPSHOT_MEMBER, json.dumps(snapshot, indent=2, ensure_ascii=False))
    return {"path": str(path), "records": len(snapshot["records"]), "format": "zip"}


def _load_snapshot(input_path):
    path = Path(input_path)
    if not path.exists():
        raise ValueError(f"backup file does not exist: {path}")
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            try:
                raw = archive.read(SNAPSHOT_MEMBER).decode("utf-8")
            except KeyError as error:
                raise ValueError("backup archive does not contain a MemCoder snapshot") from error
    else:
        raw = path.read_text(encoding="utf-8")
    try:
        snapshot = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("backup snapshot is not valid JSON") from error
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
        raise ValueError("backup snapshot has an unsupported schema version")
    for field in ("records", "provenance_edges", "plan_audits"):
        if not isinstance(snapshot.get(field), list):
            raise ValueError(f"backup snapshot field '{field}' must be a list")
    for field in ("failure_frontiers", "cognitive_branches"):
        if field in snapshot and not isinstance(snapshot[field], list):
            raise ValueError(f"backup snapshot field '{field}' must be a list")
    return snapshot


def restore_snapshot(input_path, collection=None, embedder=None):
    """Merge a snapshot; never delete local records during restore."""
    snapshot = _load_snapshot(input_path)
    from memory.audit_store import merge_audit_entries
    from memory.record_store import add_edge, get_record, save_record, rebuild_guidance_index

    records_merged = 0
    for record in snapshot["records"]:
        if not isinstance(record, dict) or not record.get("record_id"):
            continue
        existing = get_record(record["record_id"])
        if existing and int(existing.get("revision", 1)) >= int(record.get("revision", 1)):
            continue
        save_record(dict(record))
        records_merged += 1

    edges_merged = 0
    for edge in snapshot["provenance_edges"]:
        if not isinstance(edge, dict):
            continue
        try:
            edges_merged += add_edge(
                edge["source_id"], edge["target_id"], edge["relation"], edge["owner"],
                metadata=edge.get("metadata"), created_at=edge.get("created_at"),
            )
        except (KeyError, ValueError):
            continue

    audits_merged = merge_audit_entries(snapshot["plan_audits"])
    from memory.dreaming import restore_candidates
    dream_candidates_merged = restore_candidates(snapshot.get("dream_candidates", []))
    from memory.failure_frontier import restore_frontiers
    frontier_merged = restore_frontiers(snapshot.get("failure_frontiers", []))
    from memory.cognitive_branch import restore_branches
    branches_merged = restore_branches(snapshot.get("cognitive_branches", []))
    if collection is None or embedder is None:
        from memory.chroma_client import collection as active_collection
        from memory.embedder import embed
        collection = active_collection if collection is None else collection
        embedder = embed if embedder is None else embedder
    index = rebuild_guidance_index(collection, embedder)
    return {
        "mode": "merge",
        "records_merged": records_merged,
        "provenance_edges_merged": edges_merged,
        "plan_audits_merged": audits_merged,
        "dream_candidates_merged": dream_candidates_merged,
        "failure_frontiers_merged": frontier_merged,
        "cognitive_branches_merged": branches_merged,
        "index": index,
    }
