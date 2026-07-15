from memory.search import search_memory
from memory.embedder import embed
from memory.relevance import (
    filter_trusted_memories,
    memory_confidence
)


def calculate_confidence(memories):

    if not memories:
        return 0.0

    return round(
        memory_confidence(memories[0]),
        2
    )


def get_strategy(confidence):

    if confidence >= 0.85:
        return "memory_first"

    elif confidence >= 0.60:
        return "memory_guided"

    return "normal_reasoning"


def hierarchical_search(
        problem,
        agent_id="human",
        include_shared=True):

    query_embedding = embed(problem)

    experiences = search_memory(
        query_embedding=query_embedding,
        k=5,
        memory_type="experience",
        agent_id=agent_id,
        include_shared=include_shared
    )

    mistakes = search_memory(
        query_embedding=query_embedding,
        k=3,
        memory_type="mistake",
        agent_id=agent_id,
        include_shared=include_shared
    )

    principles = search_memory(
        query_embedding=query_embedding,
        k=2,
        memory_type="principle",
        agent_id=agent_id,
        include_shared=include_shared
    )

    reflections = search_memory(
        query_embedding=query_embedding,
        k=2,
        memory_type="reflection",
        agent_id=agent_id,
        include_shared=include_shared
    )

    experiences = filter_trusted_memories(
        experiences,
        query=problem
    )

    mistakes = filter_trusted_memories(
        mistakes,
        query=problem
    )

    principles = filter_trusted_memories(
        principles,
        query=problem
    )

    reflections = filter_trusted_memories(
        reflections,
        query=problem
    )

    confidence = calculate_confidence(
        experiences
    )

    strategy = get_strategy(
        confidence
    )

    return {

        "confidence": confidence,

        "strategy": strategy,

        "experiences": experiences,

        "mistakes": mistakes,

        "principles": principles,

        "reflections": reflections

    }
