from memory.consolidator import (
    find_similar_memories,
    merge_memories
)


def consolidate_memory(
        task,
        memory_type=None):

    memories = find_similar_memories(
        task,
        memory_type
    )

    if len(memories) <= 1:

        print("Nothing to consolidate.")

        return None

    merged = merge_memories(
        memories
    )

    return merged