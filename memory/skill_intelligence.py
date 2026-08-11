"""Provider-free transfer, composition, evolution, and causal credit for skills."""

import json
import os
from pathlib import Path

from memory.records import utc_now


def _terms(value):
    ignored = {"and", "for", "the", "this", "that", "with", "only", "project", "current"}
    return {
        word.lower().strip(".,:;()[]")
        for word in str(value or "").split()
        if len(word) > 2 and word.lower().strip(".,:;()[]") not in ignored
    }


def compile_transfer(definition, problem, environment=None):
    """Separate reusable procedure from assumptions that need current-project proof."""
    environment = environment or {}
    context = " ".join([problem, json.dumps(environment, sort_keys=True)])
    context_terms = _terms(context)
    preconditions = definition.get("preconditions") or [definition.get("when_to_use", "")]
    matched, missing = [], []
    for condition in preconditions:
        (matched if _terms(condition) & context_terms else missing).append(condition)
    invalid = [
        condition for condition in definition.get("applicability_limits", [])
        if _terms(condition) & context_terms
    ]
    reusable = list(definition.get("steps", [])) if not invalid else []
    adapt = [f"Verify before reuse: {condition}" for condition in missing]
    return {
        "matched_conditions": matched,
        "missing_conditions": missing,
        "invalid_assumptions": invalid,
        "reusable_steps": reusable,
        "adapt_steps": adapt,
        "failure_boundaries": list(definition.get("failure_handling", [])),
        "verification": list(definition.get("verification", [])),
        "rollback": list(definition.get("rollback", [])),
        "safe_to_apply": not invalid,
    }


def compose_skills(definitions):
    """Refuse unsafe compositions and otherwise return an explicit order."""
    if not isinstance(definitions, list) or not definitions:
        raise ValueError("definitions must contain at least one skill.")
    names = [definition.get("name", "unnamed skill") for definition in definitions]
    mutations = {}
    conflicts = []
    for definition in definitions:
        for mutation in definition.get("state_mutations", []):
            resource, separator, mode = str(mutation).partition(":")
            if not separator:
                continue
            prior = mutations.get(resource)
            if prior and prior != mode:
                conflicts.append(f"{resource}: {prior} conflicts with {mode}")
            mutations[resource] = mode
    if conflicts:
        return {"compatible": False, "skills": names, "conflicts": conflicts, "plan": []}
    return {
        "compatible": True,
        "skills": names,
        "conflicts": [],
        "plan": [
            {"order": index, "skill": definition.get("name"), "steps": definition.get("steps", [])}
            for index, definition in enumerate(definitions, start=1)
        ],
        "verification": [item for definition in definitions for item in definition.get("verification", [])],
        "rollback": [item for definition in reversed(definitions) for item in definition.get("rollback", [])],
    }


def evolve_skill(definition, changes, project_id=None):
    """Create a reviewable next version while retaining the prior version."""
    if not isinstance(changes, dict) or not changes:
        raise ValueError("changes must be a non-empty object.")
    evolved = dict(definition)
    history = list(definition.get("version_history", []))
    history.append({
        "version": definition.get("version", 1),
        "changed_fields": sorted(changes),
        "timestamp": utc_now(),
    })
    evolved.update(changes)
    evolved["version"] = int(definition.get("version", 1)) + 1
    evolved["version_history"] = history
    if project_id:
        overlays = dict(evolved.get("project_overlays", {}))
        overlays[project_id] = changes
        evolved["project_overlays"] = overlays
    return {"previous": definition, "candidate": evolved, "requires_review": True}


def _path():
    configured = os.environ.get("MEMCODER_SKILL_CREDIT_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_skill_credit.jsonl"


def _events():
    path = _path()
    if not path.exists():
        return []
    loaded = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                loaded.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return loaded


def record_causal_credit(skill_id, owner, outcome, influence, changed_steps=None, warning=None):
    """Credit a skill only when the host reports that it changed behavior."""
    if influence not in {"changed_behavior", "present_only", "ignored"}:
        raise ValueError("influence must be changed_behavior, present_only, or ignored.")
    event = {
        "skill_id": skill_id,
        "owner": owner,
        "outcome": outcome,
        "influence": influence,
        "changed_steps": list(changed_steps or []),
        "warning": warning,
        "timestamp": utc_now(),
    }
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")
    return event


def causal_summary(skill_id, owner):
    rows = [row for row in _events() if row.get("skill_id") == skill_id and row.get("owner") == owner]
    influenced = [row for row in rows if row.get("influence") == "changed_behavior"]
    return {
        "skill_id": skill_id,
        "present": len(rows),
        "influenced": len(influenced),
        "successful_influence": sum(row.get("outcome") == "succeeded" for row in influenced),
        "failed_influence": sum(row.get("outcome") == "failed" for row in influenced),
        "ignored": sum(row.get("influence") == "ignored" for row in rows),
    }
