from memory.relevance import filter_trusted_memories


trusted = {
    "task": "Validate an incoming API payload",
    "summary": "The payload was missing a required field.",
    "solution": "Validate the payload before processing it.",
    "files": ["api.py"],
    "score": 0.20,
}
untrusted = {
    "task": "Unrelated test memory",
    "summary": "This must never influence the answer.",
    "solution": "Do not use it.",
    "files": ["test.py"],
    "score": 0.90,
}

filtered = filter_trusted_memories([trusted, untrusted, {"task": "Missing distance"}])
assert [memory["task"] for memory in filtered] == [trusted["task"]]

print("PASS: retrieval safety")
