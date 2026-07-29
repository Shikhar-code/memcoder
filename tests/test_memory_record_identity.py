"""Stable IDs must survive mutations while content fingerprints may change."""

from memory.records import initialize_record, record_id, revise_record


memory = {
    "task": "Validate required project name",
    "files": ["project.py"],
    "summary": "Missing values need an explicit validation error.",
    "solution": "Check name before string processing.",
    "owner": "identity-test",
}

initialize_record(memory)
original_id = record_id(memory)
original_hash = memory["content_hash"]
assert original_id.startswith("mem_")
assert memory["revision"] == 1
assert memory["record_state"] == "trusted"

memory["solution"] = "Validate missing, null, and whitespace-only values first."
revise_record(memory)

assert record_id(memory) == original_id
assert memory["content_hash"] != original_hash
assert memory["revision"] == 2
assert memory["schema_version"] == 2

legacy = {"hash": "legacy-content-hash"}
assert record_id(legacy) == "legacy-content-hash"

print("PASS: stable memory identity and revision metadata")
