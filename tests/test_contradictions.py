"""Contradictions must withhold unsafe guidance while preserving both records."""

import os
import sys
import tempfile
import types

database = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3").name
os.unlink(database)
os.environ["MEMCODER_RECORD_DB_PATH"] = database

from memory.contradictions import report_contradiction, resolve_contradiction
from memory.provenance import trace
from memory.record_store import get_record, list_records, save_record
from memory.records import initialize_record
from memory.relevance import filter_trusted_memories


first = {
    "record_id": "mem_first",
    "task": "Use implementation A",
    "files": ["service.py"],
    "summary": "An older verified solution used implementation A.",
    "solution": "Apply implementation A.",
    "type": "experience",
    "owner": "contradiction-test",
    "score": 0.2,
}
second = {
    "record_id": "mem_second",
    "task": "Use implementation B",
    "files": ["service.py"],
    "summary": "A later verified solution used implementation B.",
    "solution": "Apply implementation B.",
    "type": "experience",
    "owner": "contradiction-test",
    "score": 0.2,
}
for record in (first, second):
    initialize_record(record)
    save_record(record)

sync = types.ModuleType("memory.index_sync")
sync.sync_record = lambda memory: None
sys.modules["memory.index_sync"] = sync

reported = report_contradiction(
    "mem_first",
    "mem_second",
    owner="contradiction-test",
    reason="The newer verified contract requires incompatible behavior.",
)
assert reported["automatic_retrieval_withheld"]
assert get_record("mem_first")["record_state"] == "contradicted"
assert get_record("mem_second")["record_state"] == "contradicted"
assert len(list_records()) == 2
assert not filter_trusted_memories([get_record("mem_first")], query="implementation")
assert any(edge["relation"] == "contradicts" for edge in trace("mem_first", "contradiction-test"))

resolved = resolve_contradiction(
    "mem_second",
    "mem_first",
    owner="contradiction-test",
    reason="The newer contract was re-verified and supersedes the old behavior.",
)
assert resolved["winner_state"] == "trusted"
assert get_record("mem_second")["record_state"] == "trusted"
assert get_record("mem_first")["record_state"] == "superseded"
assert any(edge["relation"] == "supersedes" for edge in trace("mem_second", "contradiction-test"))

print("PASS: contradiction reporting and resolution preserve evidence")
