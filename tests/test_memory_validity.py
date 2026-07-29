"""Lifecycle state and environment mismatch must prevent unsafe reuse."""

import os
import sys
import tempfile
import types

database = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3").name
os.unlink(database)
os.environ["MEMCODER_RECORD_DB_PATH"] = database

from memory.records import initialize_record
from memory.record_store import save_record
from memory.relevance import filter_trusted_memories
from memory.validity import attach_environment, set_record_validity


matching = {
    "task": "Validate a required project name",
    "files": ["project.py"],
    "summary": "A missing name must fail before normalization.",
    "solution": "Validate missing and blank values first.",
    "type": "experience",
    "owner": "validity-test",
    "score": 0.2,
}
attach_environment(matching, {
    "project_id": "project-a",
    "revision": "abc123",
    "dependencies": {"fastapi": "1.0"},
})
initialize_record(matching)
save_record(matching)

deprecated = dict(matching)
deprecated["record_id"] = "mem_deprecated"
deprecated["record_state"] = "deprecated"
deprecated["task"] = "Deprecated name validation"
initialize_record(deprecated)

wrong_project = dict(matching)
wrong_project["record_id"] = "mem_wrong_project"
wrong_project["task"] = "Other project validation"
attach_environment(wrong_project, {"project_id": "project-b", "revision": "abc123"})
initialize_record(wrong_project)

retrieved = filter_trusted_memories(
    [matching, deprecated, wrong_project],
    query="Validate required project name",
    current_environment={
        "project_id": "project-a",
        "revision": "abc123",
        "dependencies": {"fastapi": "1.0"},
    },
)
assert [memory["record_id"] for memory in retrieved] == [matching["record_id"]]
assert retrieved[0]["applicability"] == "match"

changed = filter_trusted_memories(
    [matching],
    query="Validate required project name",
    current_environment={
        "project_id": "project-a",
        "revision": "different",
        "dependencies": {"fastapi": "2.0"},
    },
)
assert changed[0]["applicability"] == "changed"
assert changed[0]["relevance_score"] < 0.95

sync = types.ModuleType("memory.index_sync")
synced = []
sync.sync_record = lambda memory: synced.append(memory["record_id"])
sys.modules["memory.index_sync"] = sync
updated = set_record_validity(
    matching["record_id"],
    "superseded",
    owner="validity-test",
    reason="A newer validated project contract replaced this record.",
)
assert updated["record_state"] == "superseded"
assert updated["revision"] == 2
assert synced == [matching["record_id"]]

print("PASS: memory validity and environment applicability")
