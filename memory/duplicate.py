from memory.memory_hash import memory_hash
from memory.chroma_client import collection


def is_duplicate(memory):

    h = memory_hash(memory)

    results = collection.get(
        ids=[h]
    )

    return len(results["ids"]) > 0