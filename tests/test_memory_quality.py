from memory.quality import (
    is_valid_experience,
    is_valid_principle,
    is_valid_reflection,
)


assert not is_valid_experience({
    "task": "unknown",
    "files": ["unknown"],
    "summary": "...",
    "solution": "Unknown",
})
assert not is_valid_reflection("Authentication failures are common.")
assert not is_valid_reflection("I implemented explicit validation before calling strip.")
assert not is_valid_reflection("I should always validate required fields first.")
assert is_valid_reflection(
    "I reproduced the KeyError before deciding where validation belonged."
)
assert is_valid_principle("Validate external input before processing it.")

print("PASS: memory quality admission")
