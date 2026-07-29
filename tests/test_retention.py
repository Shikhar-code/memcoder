"""Retention may supersede exact duplicates but must never delete evidence."""

import os
import sys
import tempfile
import types

database = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3").name
os.unlink(database)
os.environ["MEMCODER_RECORD_DB_PATH"] = database

from memory.provenance import trace
from memory.record_store import get_record, list_records, save_record
from memory.records import initialize_record
from memory.retention import apply_retention_preview, retention_preview
from memory.validity import attach_environment


canonical = {
    "record_id": "mem_canonical",
    "task": "Validate the required project name",
    "files": ["project.py"],
    "summary": "The focused test proved missing project names must fail early.",
    "solution": "Validate before normalization.",
    "type": "experience",
    "owner": "retention-test",
    "revision": 2,
}
duplicate = dict(canonical)
duplicate["record_id"] = "mem_duplicate"
duplicate["revision"] = 1
for record in (canonical, duplicate):
    attach_environment(record, {"project_id": "retention-project", "revision": "old"})
for record in (canonical, duplicate):
    initialize_record(record)
    save_record(record)

preview = retention_preview(
    owner="retention-test",
    environment={"project_id": "retention-project", "revision": "new"},
)
assert preview["safe_to_apply"]
assert len(preview["review_candidates"]) == 2
assert preview["actions"] == [{
    "action": "supersede_exact_duplicate",
    "canonical_id": "mem_canonical",
    "target_id": "mem_duplicate",
    "owner": "retention-test",
    "reason": "Exact duplicate content; preserve history and prefer the canonical record.",
    "content_hash": canonical["content_hash"],
}]

sync = types.ModuleType("memory.index_sync")
sync.sync_record = lambda memory: None
sys.modules["memory.index_sync"] = sync
applied = apply_retention_preview(preview, owner="retention-test")
assert applied["applied"] == ["mem_duplicate"]
assert applied["deleted"] == []
assert get_record("mem_duplicate")["record_state"] == "superseded"
assert len(list_records()) == 2
assert any(
    edge["relation"] == "supersedes" and edge["target_id"] == "mem_duplicate"
    for edge in trace("mem_canonical", owner="retention-test")
)

after = retention_preview(owner="retention-test")
assert not after["actions"]
assert after["already_archived"] == ["mem_duplicate"]

print("PASS: controlled retention preserves original evidence")
