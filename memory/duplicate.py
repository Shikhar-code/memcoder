from memory.memory_hash import memory_hash
from memory.chroma_client import collection


def find_duplicate(memory):
    """Find an existing record by immutable content fingerprint and owner."""

    h = memory_hash(memory)
    from memory.record_store import find_duplicate as find_durable_duplicate

    durable = find_durable_duplicate(h, memory.get("owner", "shared"))
    if durable:
        return durable

    # Beta 2.0 used this fingerprint as the Chroma ID. Preserve duplicate
    # detection for existing stores while new records use a stable record_id.
    legacy = collection.get(ids=[h], include=["metadatas"])
    legacy_metadatas = legacy.get("metadatas", [])
    if legacy_metadatas:
        return legacy_metadatas[0]

    results = collection.get(
        where={
            "$and": [
                {"content_hash": h},
                {"owner": memory.get("owner", "shared")},
            ]
        },
        include=["metadatas"],
    )
    metadatas = results.get("metadatas", [])
    return metadatas[0] if metadatas else None


def is_duplicate(memory):
    return find_duplicate(memory) is not None

    return len(results["ids"]) > 0
