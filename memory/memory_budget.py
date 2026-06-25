from memory.scorer import score_memory


def budget_memories(memories,
                    query="",
                    max_memories=5):

    sorted_memories = sorted(
        memories,
        key=lambda memory: score_memory(
            memory,
            query
        ),
        reverse=True
    )

    return sorted_memories[:max_memories]