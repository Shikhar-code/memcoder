"""Backups and merge-restore preserve local cognition without destructive replace."""

import os
import tempfile
from pathlib import Path

workspace = Path(tempfile.mkdtemp())
source_db = workspace / "source.sqlite3"
source_audit = workspace / "source-audits.jsonl"
os.environ["MEMCODER_RECORD_DB_PATH"] = str(source_db)
os.environ["MEMCODER_AUDIT_PATH"] = str(source_audit)

from memory.audit_store import append_plan_outcome
from memory.provenance import link
from memory.record_store import add_edge, save_record
from memory.records import initialize_record
from memory.storage_ops import create_backup, export_snapshot, restore_snapshot, storage_status


experience = {
    "task": "Validate the project name",
    "files": ["project.py"],
    "summary": "The focused test proved missing names must fail early.",
    "solution": "Validate before normalization.",
    "type": "experience",
    "owner": "storage-test",
}
reflection = {
    "task": "I checked the missing name path before changing validation.",
    "files": ["reflection"],
    "summary": "I checked the missing name path before changing validation.",
    "solution": "Observation",
    "type": "reflection",
    "owner": "storage-test",
}
for record in (experience, reflection):
    initialize_record(record)
    save_record(record)
link(reflection["record_id"], experience["record_id"], "derived_from", "storage-test")
append_plan_outcome({
    "id": "audit_storage_test",
    "plan_id": "plan_1234567890abcdef1234",
    "owner": "storage-test",
    "status": "succeeded",
})

assert storage_status()["records"] == 2
assert storage_status()["provenance_edges"] == 1
assert storage_status()["plan_audits"] == 1

export_path = workspace / "memcoder-export.json"
backup_path = workspace / "memcoder-backup.zip"
assert export_snapshot(export_path)["records"] == 2
assert create_backup(backup_path)["format"] == "zip"

destination_db = workspace / "destination.sqlite3"
destination_audit = workspace / "destination-audits.jsonl"
os.environ["MEMCODER_RECORD_DB_PATH"] = str(destination_db)
os.environ["MEMCODER_AUDIT_PATH"] = str(destination_audit)


class FakeCollection:
    def __init__(self):
        self.records = {}

    def get(self):
        return {"ids": list(self.records)}

    def delete(self, ids):
        for record_id in ids:
            self.records.pop(record_id, None)

    def add(self, ids, documents, embeddings, metadatas):
        for record_id, metadata in zip(ids, metadatas):
            self.records[record_id] = metadata


collection = FakeCollection()
restored = restore_snapshot(backup_path, collection=collection, embedder=lambda text: [float(len(text))])
assert restored["mode"] == "merge"
assert restored["records_merged"] == 2
assert restored["provenance_edges_merged"] == 1
assert restored["plan_audits_merged"] == 1
assert restored["index"]["indexed"] == 2
assert len(collection.records) == 2

repeated = restore_snapshot(export_path, collection=collection, embedder=lambda text: [float(len(text))])
assert repeated["records_merged"] == 0
assert repeated["provenance_edges_merged"] == 0
assert repeated["plan_audits_merged"] == 0

print("PASS: storage status, export, backup, and conservative restore")
