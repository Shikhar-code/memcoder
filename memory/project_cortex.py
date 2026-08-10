"""Bounded durable project state, decisions, resurrection, and handoff."""

import hashlib
import json
import math
import os
import re
from pathlib import Path

from memory.records import utc_now


STATE_FIELDS = (
    "facts", "hypotheses", "assumptions", "questions", "constraints", "goals",
    "risks", "important_files", "dependencies", "completed_work", "next_actions",
    "skills", "proof_paths",
)
SENSITIVE = re.compile(r"(^|_)(secret|password|token|api_key|access_key|private_key)($|_)", re.I)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|password|token|access[_-]?key|private[_-]?key)\b\s*[:=]\s*\S+"
)


def _path():
    configured = os.environ.get("MEMCODER_PROJECT_STATE_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_projects.jsonl"


def _history(project_id, owner):
    path = _path()
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("project_id") == project_id and record.get("owner") == owner:
                records.append(record)
    return records


def read_project_state(project_id, owner):
    history = _history(project_id, owner)
    return history[-1] if history else None


def _text(value, limit=280):
    value = " ".join(str(value or "").split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _state_item(item):
    if not isinstance(item, dict):
        return _text(item)
    value = _text(item.get("value") or item.get("text") or item.get("fact"))
    if not value:
        return ""
    return {
        "value": value,
        "status": item.get("status", "active"),
        "evidence": [_text(evidence) for evidence in item.get("evidence", [])[:5]],
        "expires_at": item.get("expires_at"),
    }


def _merge(old, new, limit=12):
    if not isinstance(new, list):
        raise ValueError("project state fields must be lists.")
    merged = []
    signatures = set()
    for item in [*old, *new]:
        value = _state_item(item)
        signature = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if value and signature not in signatures:
            merged.append(value)
            signatures.add(signature)
    return merged[-limit:]


def _current(values):
    now = utc_now()
    return [
        value for value in values
        if not isinstance(value, dict)
        or (
            value.get("status", "active") not in {"deprecated", "contradicted"}
            and (not value.get("expires_at") or str(value["expires_at"]) > now)
        )
    ]


def _display(value):
    return value.get("value", "") if isinstance(value, dict) else value


def _environment_delta(stored, current):
    stored, current = stored or {}, current or {}
    changed = [
        key for key in (
            "project_id", "runtime", "language", "branch", "revision",
            "architecture", "dependencies", "configuration", "important_files",
        )
        if key in stored and key in current and stored[key] != current[key]
    ]
    return {"status": "drifted" if changed else "compatible", "changed": changed}


def update_project_state(project_id, owner, update, environment=None):
    if not isinstance(update, dict):
        raise ValueError("project update must be an object.")
    previous = read_project_state(project_id, owner) or {}
    state = {
        field: _merge(previous.get("state", {}).get(field, []), update.get(field, []))
        for field in STATE_FIELDS
    }
    decisions = list(previous.get("decisions", []))
    conflicts = []
    for supplied in update.get("decisions", []):
        if not isinstance(supplied, dict) or not _text(supplied.get("decision")):
            raise ValueError("each decision must be an object with a non-empty decision.")
        decision = {
            "id": supplied.get("id") or "decision_" + hashlib.sha256(
                f"{project_id}:{supplied.get('scope', '')}:{supplied['decision']}".encode("utf-8")
            ).hexdigest()[:20],
            "decision": _text(supplied["decision"]),
            "rationale": _text(supplied.get("rationale")),
            "alternatives": [_text(item) for item in supplied.get("alternatives", [])[:5]],
            "rejected_reasons": [_text(item) for item in supplied.get("rejected_reasons", [])[:5]],
            "evidence": [_text(item) for item in supplied.get("evidence", [])[:5]],
            "scope": _text(supplied.get("scope") or "project", 120),
            "owner": _text(supplied.get("owner") or owner, 120),
            "status": supplied.get("status", "active"),
            "supersedes": supplied.get("supersedes"),
            "validity_conditions": [_text(item) for item in supplied.get("validity_conditions", [])[:5]],
            "superseding_event": _text(supplied.get("superseding_event")),
            "verification": [_text(item) for item in supplied.get("verification", [])[:5]],
            "environment": environment or {},
            "timestamp": utc_now(),
        }
        if decision["status"] not in {"active", "superseded", "deprecated"}:
            raise ValueError("decision status must be active, superseded, or deprecated.")
        for existing in decisions:
            if decision.get("supersedes") == existing.get("id"):
                existing["status"] = "superseded"
            elif existing.get("status") == "active" and existing.get("scope") == decision["scope"] and existing.get("decision") != decision["decision"]:
                conflicts.append({"existing": existing.get("id"), "incoming": decision["id"], "scope": decision["scope"]})
        decisions = [item for item in decisions if item.get("id") != decision["id"]]
        decisions.append(decision)

    stored = {
        "schema_version": 1,
        "project_id": _text(project_id, 160),
        "owner": _text(owner, 120),
        "state": state,
        "decisions": decisions[-20:],
        "conflicts": conflicts,
        "environment": environment or previous.get("environment", {}),
        "timestamp": utc_now(),
    }
    stored["id"] = "project_state_" + hashlib.sha256(
        json.dumps(stored, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:20]
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(stored, sort_keys=True, ensure_ascii=False) + "\n")
    return stored


def resurrect_project(project_id, owner, environment=None, token_budget=600):
    project = read_project_state(project_id, owner)
    if project is None:
        return {"project_id": project_id, "status": "unknown", "brief": None}
    drift = _environment_delta(project.get("environment"), environment)
    active, withheld = [], []
    for decision in project.get("decisions", []):
        decision_drift = _environment_delta(decision.get("environment"), environment)
        if decision.get("status") == "active" and decision_drift["status"] == "compatible":
            active.append(decision)
        else:
            withheld.append({"id": decision.get("id"), "reason": "inactive or environment drifted"})
    state = {key: _current(value) for key, value in project.get("state", {}).items()}
    brief = {
        "objective": _display((state.get("goals") or [""])[-1]),
        "verified_facts": state.get("facts", [])[-6:],
        "hypotheses": state.get("hypotheses", [])[-4:],
        "assumptions": state.get("assumptions", [])[-4:],
        "verified_completed_work": state.get("completed_work", [])[-5:],
        "decisions": active[-6:],
        "constraints": state.get("constraints", [])[-6:],
        "unresolved_risks": state.get("risks", [])[-5:],
        "open_questions": state.get("questions", [])[-5:],
        "important_files": state.get("important_files", [])[-8:],
        "skills": state.get("skills", [])[-5:],
        "proof_paths": state.get("proof_paths", [])[-5:],
        "next_safe_action": _display((state.get("next_actions") or ["Revalidate the current environment before continuing."])[-1]),
    }
    while math.ceil(len(json.dumps(brief, ensure_ascii=False)) / 4) > max(160, int(token_budget)):
        longest = max((key for key, value in brief.items() if isinstance(value, list) and value), key=lambda key: len(brief[key]), default=None)
        if longest is None:
            break
        brief[longest] = brief[longest][1:]
    return {
        "project_id": project_id,
        "status": "drifted" if drift["changed"] else "ready",
        "environment_delta": drift,
        "withheld_decisions": withheld,
        "brief": brief,
        "budget": {
            "estimated_tokens": math.ceil(len(json.dumps(brief, ensure_ascii=False)) / 4),
            "token_budget": max(160, int(token_budget)),
        },
    }


def _scrub(value):
    if isinstance(value, dict):
        return {key: _scrub(item) for key, item in value.items() if not SENSITIVE.search(str(key)) and key not in {"transcript", "raw_transcript"}}
    if isinstance(value, list):
        return [_scrub(item) for item in value]
    if isinstance(value, str):
        return SECRET_ASSIGNMENT.sub("[REDACTED]", value)
    return value


def export_handoff(project_id, owner, environment=None):
    resurrection = resurrect_project(project_id, owner, environment=environment)
    if resurrection["brief"] is None:
        raise ValueError("project state was not found for this agent.")
    capsule = _scrub({
        "schema_version": 1,
        "kind": "memcoder_project_handoff",
        "project_id": project_id,
        "source_owner": owner,
        "created_at": utc_now(),
        "environment": environment or {},
        "brief": resurrection["brief"],
        "withheld_decisions": resurrection["withheld_decisions"],
        "receiver_instruction": "Revalidate environment differences and supplied evidence before acting.",
    })
    if not isinstance(capsule, dict):
        raise ValueError("project handoff could not be serialized.")
    capsule["checksum"] = hashlib.sha256(
        json.dumps(capsule, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return capsule


def accept_handoff(capsule, owner, environment=None):
    if not isinstance(capsule, dict) or capsule.get("kind") != "memcoder_project_handoff":
        raise ValueError("handoff must be a MemCoder project handoff capsule.")
    supplied_checksum = capsule.get("checksum")
    unsigned = {key: value for key, value in capsule.items() if key != "checksum"}
    expected_checksum = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    if supplied_checksum != expected_checksum:
        raise ValueError("handoff checksum is missing or invalid.")
    brief = _scrub(capsule.get("brief", {}))
    if not isinstance(brief, dict):
        raise ValueError("handoff brief must be an object.")
    update = {
        "goals": [brief.get("objective", "")],
        "facts": brief.get("verified_facts", []),
        "hypotheses": brief.get("hypotheses", []),
        "assumptions": brief.get("assumptions", []),
        "completed_work": brief.get("verified_completed_work", []),
        "constraints": brief.get("constraints", []),
        "risks": brief.get("unresolved_risks", []),
        "questions": brief.get("open_questions", []),
        "important_files": brief.get("important_files", []),
        "skills": brief.get("skills", []),
        "proof_paths": brief.get("proof_paths", []),
        "next_actions": [brief.get("next_safe_action", "")],
        "decisions": brief.get("decisions", []),
    }
    stored = update_project_state(capsule.get("project_id", ""), owner, update, environment=environment)
    return {
        "accepted": True,
        "project_id": stored["project_id"],
        "state_id": stored["id"],
        "environment_delta": _environment_delta(capsule.get("environment"), environment),
        "instruction": "Revalidate imported state before use.",
    }
