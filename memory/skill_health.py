"""Derived trust state for Skills from linked, QA-audited plan outcomes."""

import json


REVIEW_FAILURE_COUNT = 2


def skill_health(skill_id, agent_id="automation"):
    """Calculate a conservative, owner-scoped health state without mutation."""
    if not isinstance(skill_id, str) or not skill_id.strip():
        raise ValueError("skill_id must be a non-empty string.")

    from memory.chroma_client import collection

    result = collection.get(
        where={
            "$and": [
                {"type": "plan_outcome"},
                {"applied_skill_id": skill_id},
                {"owner": agent_id},
            ]
        },
        include=["metadatas"],
    )
    statuses = []
    for metadata in result.get("metadatas", []):
        try:
            verification = json.loads(metadata.get("verification", ""))
        except (TypeError, json.JSONDecodeError):
            verification = {}
        statuses.append(verification.get("status", metadata.get("plan_status", "unknown")))

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
