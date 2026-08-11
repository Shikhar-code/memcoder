"""Provider-free promotion of QA-approved experiences into reusable skills."""

import json

from memory.records import record_id


SKILL_SCHEMA_VERSION = 2
SUPPORTED_SKILL_SCHEMA_VERSIONS = {1, 2}


def _required_text(value, field, minimum_words=1):
    if not isinstance(value, str) or len(value.strip().split()) < minimum_words:
        raise ValueError(f"Skill field '{field}' must be meaningful.")
    return " ".join(value.split())


def _string_list(value, field, minimum_items=1):
    if not isinstance(value, list) or len(value) < minimum_items:
        raise ValueError(f"Skill field '{field}' must contain at least {minimum_items} item(s).")
    normalized = []
    for item in value:
        normalized.append(_required_text(item, field))
    return normalized


def _optional_string_list(value, field):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"Skill field '{field}' must be a list.")
    return [_required_text(item, field) for item in value]


def is_valid_skill_definition(definition):
    """Return whether stored Skill metadata is safe to expose as a procedure."""
    if not isinstance(definition, dict):
        return False
    if definition.get("schema_version") not in SUPPORTED_SKILL_SCHEMA_VERSIONS:
        return False
    if not isinstance(definition.get("name"), str) or len(definition["name"].split()) < 2:
        return False
    if not isinstance(definition.get("when_to_use"), str) or len(definition["when_to_use"].split()) < 3:
        return False
    for field, minimum_items in (("inputs", 1), ("steps", 2), ("verification", 1), ("supporting_experience_ids", 1)):
        values = definition.get(field)
        if not isinstance(values, list) or len(values) < minimum_items:
            return False
        if any(not isinstance(value, str) or not value.strip() for value in values):
            return False
    principle_ids = definition.get("supporting_principle_ids", [])
    if not isinstance(principle_ids, list):
        return False
    if any(not isinstance(value, str) or not value.strip() for value in principle_ids):
        return False
    if definition.get("schema_version") == 2:
        if not isinstance(definition.get("purpose"), str) or not definition["purpose"].strip():
            return False
        for field in (
                "preconditions", "decision_points", "expected_observations",
                "failure_handling", "rollback", "applicability_limits",
                "state_mutations", "resources", "version_history"):
            if not isinstance(definition.get(field), list):
                return False
        if not isinstance(definition.get("project_overlays"), dict):
            return False
        if not isinstance(definition.get("health"), str):
            return False
    return (
        isinstance(definition.get("human_approved"), bool)
        and isinstance(definition.get("version"), int)
        and definition["version"] >= 1
    )


def _qa_approved(metadata):
    try:
        verification = json.loads(metadata.get("verification", ""))
    except (TypeError, json.JSONDecodeError):
        return False
    return verification.get("qa_verdict") == "approved"


def _supporting_experiences(ids, agent_id):
    from memory.chroma_client import collection

    result = collection.get(ids=ids, include=["metadatas"])
    found = dict(zip(result.get("ids", []), result.get("metadatas", [])))
    approved = []
    rejected = []
    for experience_id in ids:
        metadata = found.get(experience_id)
        if not isinstance(metadata, dict):
            rejected.append(f"{experience_id}: not found")
        elif metadata.get("type") != "experience":
            rejected.append(f"{experience_id}: not an experience")
        elif metadata.get("owner") not in {agent_id, "shared"}:
            rejected.append(f"{experience_id}: not accessible to this agent")
        elif not _qa_approved(metadata):
            rejected.append(f"{experience_id}: missing QA-approved verification")
        else:
            approved.append(metadata)
    return approved, rejected


def _supporting_principles(ids, agent_id):
    if not ids:
        return [], []

    from memory.chroma_client import collection

    result = collection.get(ids=ids, include=["metadatas"])
    found = dict(zip(result.get("ids", []), result.get("metadatas", [])))
    supporting = []
    rejected = []
    for principle_id in ids:
        metadata = found.get(principle_id)
        if not isinstance(metadata, dict):
            rejected.append(f"{principle_id}: not found")
        elif metadata.get("type") != "principle":
            rejected.append(f"{principle_id}: not a principle")
        elif metadata.get("owner") not in {agent_id, "shared"}:
            rejected.append(f"{principle_id}: not accessible to this agent")
        else:
            supporting.append(metadata)
    return supporting, rejected


def promote_skill(
        name,
        when_to_use,
        inputs,
        steps,
        verification,
        supporting_experience_ids,
        supporting_principle_ids=None,
        agent_id="automation",
        human_approved=False,
        purpose=None,
        preconditions=None,
        decision_points=None,
        expected_observations=None,
        failure_handling=None,
        rollback=None,
        applicability_limits=None,
        state_mutations=None,
        resources=None):
    """Promote a procedure only when its supporting evidence is trustworthy."""
    name = _required_text(name, "name", minimum_words=2)
    when_to_use = _required_text(when_to_use, "when_to_use", minimum_words=3)
    inputs = _string_list(inputs, "inputs")
    steps = _string_list(steps, "steps", minimum_items=2)
    verification = _string_list(verification, "verification")
    support_ids = _string_list(supporting_experience_ids, "supporting_experience_ids")
    principle_ids = _optional_string_list(
        supporting_principle_ids,
        "supporting_principle_ids",
    )
    human_approved = bool(human_approved)
    purpose = _required_text(purpose or name, "purpose")
    preconditions = _optional_string_list(
        preconditions if preconditions is not None else [when_to_use], "preconditions"
    )
    decision_points = _optional_string_list(decision_points, "decision_points")
    expected_observations = _optional_string_list(
        expected_observations, "expected_observations"
    )
    failure_handling = _optional_string_list(
        failure_handling if failure_handling is not None
        else ["Stop and investigate when an expected observation is absent."],
        "failure_handling",
    )
    rollback = _optional_string_list(
        rollback if rollback is not None else ["Revert the skill's current-project changes."],
        "rollback",
    )
    applicability_limits = _optional_string_list(applicability_limits, "applicability_limits")
    state_mutations = _optional_string_list(state_mutations, "state_mutations")
    resources = _optional_string_list(resources, "resources")

    supporting, rejected = _supporting_experiences(support_ids, agent_id)
    if rejected:
        raise ValueError("Skill promotion rejected: " + "; ".join(rejected))
    if len(supporting) < 2 and not human_approved:
        raise ValueError(
            "Skill promotion requires at least two QA-approved experiences, "
            "or one QA-approved experience with human_approved=true."
        )
    _, principle_rejected = _supporting_principles(principle_ids, agent_id)
    if principle_rejected:
        raise ValueError("Skill promotion rejected: " + "; ".join(principle_rejected))

    definition = {
        "schema_version": SKILL_SCHEMA_VERSION,
        "name": name,
        "when_to_use": when_to_use,
        "inputs": inputs,
        "steps": steps,
        "verification": verification,
        "supporting_experience_ids": support_ids,
        "supporting_principle_ids": principle_ids,
        "human_approved": human_approved,
        "version": 1,
        "purpose": purpose,
        "preconditions": preconditions,
        "decision_points": decision_points,
        "expected_observations": expected_observations,
        "failure_handling": failure_handling,
        "rollback": rollback,
        "applicability_limits": applicability_limits,
        "state_mutations": state_mutations,
        "resources": resources,
        "version_history": [],
        "project_overlays": {},
        "health": "unproven",
    }
    if not is_valid_skill_definition(definition):
        raise ValueError("Skill promotion produced an invalid skill definition.")

    from memory.extractor import extract_memory
    from memory.store import add_memory
    from memory.provenance import link

    memory = extract_memory(
        task=name,
        files=["skill"],
        summary=f"Use when: {when_to_use}",
        solution="\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1)),
        importance=10,
        memory_type="skill",
        verification=json.dumps({
            "qa_verdict": "approved",
            "promotion": "QA-approved supporting experiences",
        }, sort_keys=True),
    )
    memory["owner"] = agent_id
    memory["skill_definition"] = json.dumps(definition, sort_keys=True)
    memory["supporting_experience_ids"] = json.dumps(support_ids)
    memory["supporting_principle_ids"] = json.dumps(principle_ids)
    stored = add_memory(memory)
    skill_id = record_id(stored)
    for support_id in support_ids + principle_ids:
        link(support_id, skill_id, "supports", agent_id)
    return {
        "promoted": True,
        "skill": definition,
        "id": skill_id,
        "supporting_experience_count": len(supporting),
    }


def skill_definition(memory):
    """Decode a stored skill safely for host output."""
    try:
        definition = json.loads(memory.get("skill_definition", ""))
    except (TypeError, json.JSONDecodeError):
        return None
    return definition if is_valid_skill_definition(definition) else None
