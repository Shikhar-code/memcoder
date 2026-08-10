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
        include_shared=True,
        include_skills=True,
        environment=None,
        utility_threshold=None):

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

    skills = []
    if include_skills:
        skills = search_memory(
            query_embedding=query_embedding,
            k=3,
            memory_type="skill",
            agent_id=agent_id,
            include_shared=include_shared
        )

    experiences = filter_trusted_memories(
        experiences,
        query=problem,
        current_environment=environment,
    )

    mistakes = filter_trusted_memories(
        mistakes,
        query=problem,
        current_environment=environment,
    )

    principles = filter_trusted_memories(
        principles,
        query=problem,
        current_environment=environment,
    )

    reflections = filter_trusted_memories(
        reflections,
        query=problem,
        current_environment=environment,
    )

    if include_skills:
        skills = filter_trusted_memories(
            skills,
            query=problem,
            current_environment=environment,
        )

        # A vector match alone must never turn malformed metadata into a procedure.
        from memory.skills import skill_definition
        skills = [skill for skill in skills if skill_definition(skill) is not None]

        # Repeated QA-rejected executions require review before automatic reuse.
        from memory.skill_health import eligible_skills
        skills = eligible_skills(skills, agent_id=agent_id)

    confidence = calculate_confidence(
        experiences
    )

    strategy = get_strategy(
        confidence
    )

    results = {

        "confidence": confidence,

        "strategy": strategy,

        "experiences": experiences,

        "mistakes": mistakes,

        "principles": principles,

        "reflections": reflections,
        "skills": skills,

    }
    from memory.utility import apply_utility_policy
    return apply_utility_policy(
        results,
        problem,
        owner=agent_id,
        threshold=utility_threshold,
        environment=environment,
    )
