import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)

from memory.parse_everything import parse_everything
from memory.quality import (
    is_valid_experience,
    is_valid_principle,
    is_valid_reflection
)


valid_output = """EXPERIENCE
TASK:
Validate incoming API payload
FILES:
api.py
SUMMARY:
A required payload field was missing during request processing.
SOLUTION:
Validate required fields before processing the request.
-------------------
REFLECTIONS
1. I checked the request shape before changing application code.
-------------------
PRINCIPLES
1. Validate external input before processing it.
-------------------
MISTAKES
TASK:
Assumed the payload was complete
FILES:
api.py
SUMMARY:
The request was processed before required fields were checked.
SOLUTION:
Validate required fields at the API boundary.
"""

parsed = parse_everything(valid_output)

assert is_valid_experience(parsed["experience"])
assert len(parsed["mistakes"]) == 1
assert is_valid_experience(parsed["mistakes"][0])
assert is_valid_reflection(parsed["reflections"][0])
assert is_valid_principle(parsed["principles"][0])

malformed = parse_everything(
    "REFLECTIONS\n1. I guessed before checking evidence."
)

assert malformed["experience"] is None
assert malformed["mistakes"] == []
assert not is_valid_experience({
    "task": "unknown",
    "files": ["unknown"],
    "summary": "...",
    "solution": "Unknown"
})
assert not is_valid_reflection(
    "Authentication failures are common."
)
assert not is_valid_reflection(
    "I implemented explicit validation before calling strip."
)
assert not is_valid_reflection(
    "I should always validate required fields first."
)
assert is_valid_reflection(
    "I reproduced the KeyError before deciding where validation belonged."
)

print("PASS: memory quality admission")
