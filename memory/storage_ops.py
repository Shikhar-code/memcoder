"""Portable, conservative operational controls for local MemCoder storage."""

import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


SNAPSHOT_SCHEMA_VERSION = 1
SNAPSHOT_MEMBER = "memcoder_snapshot.json"


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def storage_status():
    from memory.audit_store import list_audit_entries
    from memory.record_store import list_edges, list_records, storage_path

    records = list_records()
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
    }


def build_snapshot():
    from memory.audit_store import list_audit_entries
    from memory.record_store import list_edges, list_records

    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "exported_at": _utc_now(),
        "records": list_records(),
        "provenance_edges": list_edges(),
        "plan_audits": list_audit_entries(),
    }


def export_snapshot(output_path):
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
        "index": index,
    }
