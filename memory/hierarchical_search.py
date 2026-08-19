import os

from memory.record_store import has_records
from memory.chroma_client import collection
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


def embed(text):
    """Load the embedding provider only when a non-empty store needs it."""
    from memory.embedder import embed as _embed
    return _embed(text)


def hierarchical_search(
        problem,
        agent_id="human",
        include_shared=True,
        include_skills=True,
        environment=None,
        utility_threshold=None):

    from memory.policy import evaluate_retrieval
    retrieval_policy = evaluate_retrieval(
        owner=agent_id,
        project_id=(environment or {}).get("project_id") if isinstance(environment, dict) else None,
        include_shared=include_shared,
    )
    requested_include_shared = include_shared
    if not retrieval_policy["allowed"]:
        include_shared = False

    # Do not load an embedding model just to discover an empty local store.
    try:
        from memory.chroma_client import active_db_path
        if not has_records() and not active_db_path().exists():
            empty = {
                "confidence": 0.0,
                "strategy": "normal_reasoning",
                "experiences": [],
                "mistakes": [],
                "principles": [],
                "reflections": [],
                "skills": [],
                "policy": {
                    "retrieval": retrieval_policy,
                    "requested_include_shared": requested_include_shared,
                },
            }
            from memory.utility import apply_utility_policy
            return apply_utility_policy(
                empty,
                problem,
                owner=agent_id,
                threshold=utility_threshold,
                environment=environment,
            )
    except Exception:
        # Storage failures remain fail-open; the normal search path owns the error.
        pass

    from memory.record_store import search_records_lexical

    limits = {
        "experience": 5,
        "mistake": 3,
        "principle": 2,
        "reflection": 2,
        "skill": 3,
    }
    try:
        candidates = {
            kind: search_records_lexical(
                problem,
                owner=agent_id,
                include_shared=include_shared,
                record_type=kind,
                limit=limit,
            )
            for kind, limit in limits.items()
            if include_skills or kind != "skill"
        }
        lexical_error = None
    except Exception as error:
        candidates = {
            kind: [] for kind in limits if include_skills or kind != "skill"
        }
        lexical_error = type(error).__name__
    retrieval = {
        "backend": "lexical",
        "semantic_warm": False,
        "fallback": f"lexical_unavailable:{lexical_error}" if lexical_error else None,
    }

    # Persistent MCP hosts prewarm semantic retrieval in the background. A
    # one-shot CLI call never pays the cold model-load cost unless explicitly
    # requested.
    import memory.embedder as embedder_module
    warm_check = getattr(embedder_module, "is_warm", None)
    semantic_warm = bool(warm_check()) if warm_check else False
    semantic_allowed = semantic_warm or warm_check is None or os.environ.get(
        "MEMCODER_ALLOW_COLD_SEMANTIC", ""
    ).lower() in {"1", "true", "yes"}
    retrieval["semantic_warm"] = semantic_warm
    if semantic_allowed:
        try:
            from memory.search import search_memory
            query_embedding = embed(problem)
            for kind, limit in limits.items():
                if kind == "skill" and not include_skills:
                    continue
                semantic = search_memory(
                    query_embedding=query_embedding,
                    k=limit,
                    memory_type=kind,
                    agent_id=agent_id,
                    include_shared=include_shared,
                )
                by_id = {item.get("id"): item for item in semantic}
                for item in candidates.get(kind, []):
                    by_id.setdefault(item.get("id"), item)
                candidates[kind] = list(by_id.values())[:limit]
            retrieval["backend"] = "semantic+lexical"
        except Exception as error:
            retrieval["fallback"] = f"semantic_unavailable:{type(error).__name__}"
    else:
        retrieval["fallback"] = "semantic_cold"

    experiences = candidates.get("experience", [])
    mistakes = candidates.get("mistake", [])
    principles = candidates.get("principle", [])
    reflections = candidates.get("reflection", [])
    skills = candidates.get("skill", [])

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
        "policy": {"retrieval": retrieval_policy, "requested_include_shared": requested_include_shared},
        "retrieval": retrieval,

    }
    from memory.utility import apply_utility_policy
    return apply_utility_policy(
        results,
        problem,
        owner=agent_id,
        threshold=utility_threshold,
        environment=environment,
    )
