import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)

from context.hierarchical_context_builder import (
    build_hierarchical_context
)
from memory.relevance import filter_trusted_memories


trusted = {
    "task": "Validate an incoming API payload",
    "summary": "The payload was missing a required field.",
    "solution": "Validate the payload before processing it.",
    "files": ["api.py"],
    "score": 0.20
}

untrusted = {
    "task": "Unrelated test memory",
    "summary": "This must never influence the answer.",
    "solution": "Do not use it.",
    "files": ["test.py"],
    "score": 0.90
}

malformed = {
    "task": "Missing distance"
}

filtered = filter_trusted_memories(
    [trusted, untrusted, malformed]
)

assert [memory["task"] for memory in filtered] == [
    trusted["task"]
]

context = build_hierarchical_context({
    "experiences": [trusted, untrusted],
    "mistakes": [],
    "principles": [],
    "reflections": [
        {
            "task": "I inspect input before changing code.",
            "summary": "I inspect input before changing code.",
            "score": 0.20
        },
        {
            "task": "I ignore evidence.",
            "summary": "I ignore evidence.",
            "score": 0.90
        }
    ]
})

assert trusted["task"] in context
assert untrusted["task"] not in context
assert "Use these observations to choose what to verify first." in context
assert "I inspect input before changing code." in context
assert "I ignore evidence." not in context

print("PASS: retrieval safety")
