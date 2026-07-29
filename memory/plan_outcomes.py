"""Durable, non-guidance audit records for bounded plan execution."""

from uuid import uuid4


PLAN_OUTCOME_SCHEMA_VERSION = 1


def _status_for(qa_report):
    verdict = qa_report.get("verdict") if isinstance(qa_report, dict) else "missing"
    if verdict == "approved":
        return "succeeded"
    if verdict == "rejected":
        return "failed"
    return "unverified"


def record_plan_outcome(
        plan_id,
        task,
        qa_report,
        agent_id="automation",
        applied_skill_id=None):
    """Persist a plan audit without making it eligible as retrieval guidance."""
    if not isinstance(plan_id, str) or not plan_id.startswith("plan_"):
        raise ValueError("plan_id must be a MemCoder plan identifier.")
    if applied_skill_id is not None and not isinstance(applied_skill_id, str):
        raise ValueError("applied_skill_id must be a string when provided.")

    verdict = qa_report.get("verdict") if isinstance(qa_report, dict) else "missing"
    status = _status_for(qa_report)
    evidence_summary = qa_report.get("evidence_summary", {}) if isinstance(qa_report, dict) else {}
    verification = {
        "schema_version": PLAN_OUTCOME_SCHEMA_VERSION,
        "plan_id": plan_id,
        "status": status,
        "qa_verdict": verdict,
        "evidence_summary": evidence_summary,
    }

    from memory.audit_store import append_plan_outcome

    stored = append_plan_outcome({
        "id": f"audit_{uuid4().hex}",
        "schema_version": PLAN_OUTCOME_SCHEMA_VERSION,
        "plan_id": plan_id,
        "task": task,
        "owner": agent_id,
        "status": status,
        "qa_verdict": verdict,
        "evidence_summary": evidence_summary,
        "applied_skill_id": applied_skill_id,
        "verification": verification,
    })
    return {
        "id": stored["id"],
        "plan_id": plan_id,
        "status": status,
        "qa_verdict": verdict,
        "applied_skill_id": applied_skill_id,
    }


def plan_outcome_history(plan_id, agent_id="automation"):
    """Return owner-scoped audit entries for one plan, newest first."""
    if not isinstance(plan_id, str) or not plan_id.startswith("plan_"):
        raise ValueError("plan_id must be a MemCoder plan identifier.")

    from memory.audit_store import plan_outcome_history as load_history
    return load_history(plan_id, agent_id)
