"""Provenance links must be explicit, typed, and durable."""

import os
import tempfile

database = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3").name
os.unlink(database)
os.environ["MEMCODER_RECORD_DB_PATH"] = database

from memory.provenance import link, trace
from memory.record_store import save_record
from memory.records import initialize_record


experience = {
    "task": "Validate a required project name",
    "files": ["project.py"],
    "summary": "The focused test proved missing names must fail early.",
    "solution": "Validate before normalization.",
    "type": "experience",
    "owner": "provenance-test",
}
reflection = {
    "task": "I checked the missing-key path before changing the validation.",
    "files": ["reflection"],
    "summary": "I checked the missing-key path before changing the validation.",
    "solution": "Observation",
    "type": "reflection",
    "owner": "provenance-test",
}
skill = {
    "task": "Required name validation",
    "files": ["skill"],
    "summary": "Use for required names before normalization.",
    "solution": "Validate, normalize, then test.",
    "type": "skill",
    "owner": "provenance-test",
}
for record in (experience, reflection, skill):
    initialize_record(record)
    save_record(record)

link(reflection["record_id"], experience["record_id"], "derived_from", "provenance-test")
link(experience["record_id"], skill["record_id"], "supports", "provenance-test")
link(experience["record_id"], "audit_approved_run", "validated_by", "provenance-test")

experience_trace = trace(experience["record_id"], owner="provenance-test")
assert {(edge["relation"], edge["direction"]) for edge in experience_trace} == {
    ("derived_from", "incoming"),
    ("supports", "outgoing"),
    ("validated_by", "outgoing"),
}

try:
    link(experience["record_id"], skill["record_id"], "invented_relation", "provenance-test")
except ValueError as error:
    assert "Unsupported provenance relation" in str(error)
else:
    raise AssertionError("Unknown provenance relations must be rejected")

print("PASS: durable typed provenance graph")
