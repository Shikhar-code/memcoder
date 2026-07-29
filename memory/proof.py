"""Build inspectable proof contracts for retrieved guidance."""

import json


def _json_object(value):
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value or "")
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _environment_conditions(memory):
    environment = _json_object(memory.get("environment"))
    if not environment:
        return ["No environment fingerprint was stored; confirm current-project applicability."]
    conditions = []
    if environment.get("project_id"):
        conditions.append(f"Applies to project: {environment['project_id']}.")
    if environment.get("fingerprint"):
        conditions.append("Confirm the current project fingerprint has not materially changed.")
    return conditions or ["Confirm current-project applicability."]


def _required_verification(memory):
    skill_definition = _json_object(memory.get("skill_definition"))
    if isinstance(skill_definition.get("verification"), list):
        checks = [str(check).strip() for check in skill_definition["verification"] if str(check).strip()]
        if checks:
            return checks

    verification = _json_object(memory.get("verification"))
    playbook = verification.get("verification_playbook")
    if isinstance(playbook, list):
        checks = []
        for check in playbook:
            if not isinstance(check, dict):
                continue
            command = str(check.get("command", "")).strip()
            assertion = str(check.get("assertion", "")).strip()
            name = str(check.get("name", "")).strip()
            if command:
                checks.append(f"Run: {command}")
            elif assertion:
                checks.append(f"Confirm: {assertion}")
            elif name:
                checks.append(f"Repeat: {name}")
        if checks:
            return checks
    if verification.get("qa_verdict") == "approved":
        return ["Repeat an equivalent current-project verification before recording new learning."]
    return ["Verify the current result with a focused test, build, assertion, or documented review."]


def _evidence(memory):
    evidence = []
    for edge in memory.get("provenance", []):
        relation = edge.get("relation")
        related_id = edge.get("target_id") if edge.get("direction") == "outgoing" else edge.get("source_id")
        if relation and related_id:
            evidence.append({"relation": relation, "record_id": related_id})

    verification = _json_object(memory.get("verification"))
    if verification.get("qa_verdict"):
        evidence.append({"relation": "qa_verdict", "value": verification["qa_verdict"]})
    return evidence


def build_proof(memory):
    """Return the evidence and limits that make a retrieved memory reusable."""
    applicability = memory.get("applicability", "unknown")
    risks = []
    if applicability == "changed":
        risks.append("The project fingerprint changed since this memory was verified.")
    elif applicability == "unknown":
        risks.append("Applicability is unconfirmed because environment context is incomplete.")
    if memory.get("validity_reason"):
        risks.append(str(memory["validity_reason"]))
    if any(edge.get("relation") == "contradicts" for edge in memory.get("provenance", [])):
        risks.append("A linked record contradicts this guidance; inspect both before reuse.")

    evidence = _evidence(memory)
    verification = _required_verification(memory)
    state = memory.get("record_state", "trusted")
    summary = (
        f"{state}; {applicability}; {len(evidence)} evidence link(s); "
        f"verify: {verification[0]}"
    )
    return {
        "record_state": state,
        "applicability": applicability,
        "evidence": evidence,
        "conditions": _environment_conditions(memory),
        "risks": risks,
        "required_verification": verification,
        "summary": summary,
    }
