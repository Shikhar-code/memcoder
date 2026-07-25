"""Durable, non-guidance audit records for bounded plan execution."""

import json


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

    from memory.capture import capture_memory

    stored = capture_memory(
        task=f"Plan outcome: {task}",
        files=["plan_outcome"],
        summary=f"Plan {plan_id} finished with status: {status}.",
        solution="Audit record only; this result is not retrieval guidance.",
        importance=1,
        memory_type="plan_outcome",
        owner=agent_id,
        verification=json.dumps(verification, sort_keys=True),
        metadata={
            "plan_id": plan_id,
            "plan_status": status,
            "applied_skill_id": applied_skill_id or "",
        },
    )
    return {
        "id": stored.get("hash", ""),
        "plan_id": plan_id,
        "status": status,
        "qa_verdict": verdict,
        "applied_skill_id": applied_skill_id,
    }


def plan_outcome_history(plan_id, agent_id="automation"):
    """Return owner-scoped audit entries for one plan, newest first."""
    if not isinstance(plan_id, str) or not plan_id.startswith("plan_"):
        raise ValueError("plan_id must be a MemCoder plan identifier.")

    from memory.chroma_client import collection

    result = collection.get(
        where={
            "$and": [
                {"type": "plan_outcome"},
                {"plan_id": plan_id},
                {"owner": agent_id},
            ]
        },
        include=["metadatas"],
    )
    entries = []
    for entry_id, metadata in zip(result.get("ids", []), result.get("metadatas", [])):
        try:
            verification = json.loads(metadata.get("verification", ""))
        except (TypeError, json.JSONDecodeError):
            verification = {}
        entries.append({
            "id": entry_id,
            "plan_id": metadata.get("plan_id", plan_id),
            "status": metadata.get("plan_status", "unknown"),
            "applied_skill_id": metadata.get("applied_skill_id") or None,
            "qa_verdict": verification.get("qa_verdict", "missing"),
            "timestamp": metadata.get("timestamp", ""),
        })
    return sorted(entries, key=lambda entry: entry["timestamp"], reverse=True)
