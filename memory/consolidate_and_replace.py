from memory.consolidator import (
    find_similar_memories,
    merge_memories
)

from memory.find_duplicate_ids import (
    find_duplicate_ids
)

from memory.delete_memories import (
    delete_memories
)

from memory.store import add_memory


def consolidate_and_replace(
        task,
        memory_type,
        owner="human",
        execute=False,
        verbose=False):

    memories = find_similar_memories(
        task,
        memory_type,
        owner=owner
    )

    if len(memories) <= 1:

        if verbose:
            print("Nothing to consolidate.")

        return None

    merged = merge_memories(
        memories
    )

    duplicate_ids = find_duplicate_ids(
        task,
        memory_type,
        owner=owner
    )

    if verbose:

        print()
        print("=== MERGED MEMORY ===")
        print(merged)

        print()
        print("=== IDS TO DELETE ===")
        print(duplicate_ids)

        print()
        print(
            "Count:",
            len(duplicate_ids)
        )

    if not execute:

        if verbose:

            print()
            print(
                "Preview only. No changes made."
            )

        return merged

    delete_memories(
        duplicate_ids,
        verbose=verbose
    )

    add_memory(
        merged,
        verbose=verbose
    )

    if verbose:

        print()
        print(
            "Consolidation complete."
        )

    return merged
