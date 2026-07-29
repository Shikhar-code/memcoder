"""Equivalent memories with an executable proof path should rank first."""

from memory.relevance import rank_memories


without_playbook = {
    "id": "memory-without-playbook",
    "task": "Validate required project name",
    "summary": "Missing names need validation before normalization.",
    "solution": "Validate before calling strip.",
    "files": ["project.py"],
    "score": 0.4,
}
with_playbook = {
    **without_playbook,
    "id": "memory-with-playbook",
    "proof": {
        "required_verification": ["Run: python test_project_name.py"],
    },
}

ranked = rank_memories(
    [without_playbook, with_playbook],
    query="Validate required project name",
)
assert [memory["id"] for memory in ranked] == [
    "memory-with-playbook",
    "memory-without-playbook",
]
assert ranked[0]["verification_strength"] == 0.10

print("PASS: verification-first retrieval ranking")
