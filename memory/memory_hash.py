import hashlib


def memory_hash(memory):

    text = (
        str(memory.get("task", "")).strip().lower()
        + "|"
        + str(memory.get("summary", "")).strip().lower()
        + "|"
        + str(memory.get("solution", "")).strip().lower()
        + "|"
        + str(memory.get("owner", "shared")).strip().lower()
    )

    return hashlib.md5(
        text.encode()
    ).hexdigest()