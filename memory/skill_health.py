"""Derived trust state for Skills from linked, QA-audited plan outcomes."""


REVIEW_FAILURE_COUNT = 2


def skill_health(skill_id, agent_id="automation"):
    """Calculate a conservative, owner-scoped health state without mutation."""
    if not isinstance(skill_id, str) or not skill_id.strip():
        raise ValueError("skill_id must be a non-empty string.")

    from memory.audit_store import outcomes_for_skill

    statuses = [
        entry.get("status", "unknown")
        for entry in outcomes_for_skill(skill_id, agent_id)
    ]

    succeeded = statuses.count("succeeded")
    failed = statuses.count("failed")
    unverified = statuses.count("unverified")
    completed = succeeded + failed
    if failed >= REVIEW_FAILURE_COUNT and failed >= succeeded:
        state = "review_required"
    elif completed == 0:
        state = "unproven"
    elif succeeded / completed >= 0.70:
        state = "trusted"
    else:
        state = "monitor"

    return {
        "skill_id": skill_id,
        "status": state,
        "attempts": len(statuses),
        "succeeded": succeeded,
        "failed": failed,
        "unverified": unverified,
        "success_rate": round(succeeded / completed, 2) if completed else None,
        "automatic_retrieval_allowed": state != "review_required",
    }


def eligible_skills(skills, agent_id, health_lookup=skill_health):
    """Annotate skills with health and exclude ones requiring human review."""
    eligible = []
    for skill in skills:
        health = health_lookup(skill.get("id", ""), agent_id=agent_id)
        annotated = dict(skill)
        annotated["health"] = health
        if health["automatic_retrieval_allowed"]:
            eligible.append(annotated)
    return eligible
