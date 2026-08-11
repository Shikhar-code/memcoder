"""Provider-free, append-only warnings for verified failure mechanisms."""

import hashlib
import json
import os
from pathlib import Path

from memory.records import utc_now
from memory.relevance import query_terms
from memory.validity import normalize_environment


STATUSES = {"candidate", "active", "stale", "rejected"}
OUTCOMES = {"helpful", "ignored", "misleading", "harmful"}


def _path():
    configured = os.environ.get("MEMCODER_FAILURE_FRONTIER_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_failure_frontier.jsonl"


def _read():
    path = _path()
    if not path.exists():
        return []
    latest = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict) and item.get("id"):
                latest[item["id"]] = item
    return list(latest.values())


def _append(item):
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    stored = {**item, "updated_at": utc_now()}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(stored, sort_keys=True, ensure_ascii=False) + "\n")
    return stored


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string.")
    return " ".join(value.split())


def _list(value, field):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list when provided.")
    return [" ".join(str(item).split()) for item in value if str(item).strip()]


def _environment(environment):
    return normalize_environment(environment) if environment is not None else None


def record_frontier(
        trigger,
        risk,
        warning,
        verification,
        owner="automation",
        environment=None,
        counterexamples=None,
        source_memory_ids=None,
        status="active"):
    """Record one observed failure mechanism without making it trusted guidance."""
    if status not in STATUSES:
        raise ValueError("status must be candidate, active, stale, or rejected.")
    owner = _text(owner, "owner")
    fields = {
        "trigger": _text(trigger, "trigger"),
        "risk": _text(risk, "risk"),
        "warning": _text(warning, "warning"),
        "verification": _text(verification, "verification"),
    }
    environment = _environment(environment)
    material = json.dumps(
        {"owner": owner, **fields, "environment": environment or {}},
        sort_keys=True, ensure_ascii=False,
    )
    frontier_id = "frontier_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:20]
    prior = next((item for item in _read() if item.get("id") == frontier_id), None)
    item = {
        "schema_version": 1,
        "id": frontier_id,
        "owner": owner,
        **fields,
        "counterexamples": _list(counterexamples, "counterexamples"),
        "source_memory_ids": _list(source_memory_ids, "source_memory_ids"),
        "environment": environment or {},
        "status": status,
        "feedback": (prior or {}).get("feedback", []),
        "created_at": (prior or {}).get("created_at") or utc_now(),
    }
    return _append(item)


def list_frontiers(owner=None, status=None):
    if status is not None and status not in STATUSES:
        raise ValueError("status must be candidate, active, stale, or rejected.")
    return sorted([
        item for item in _read()
        if (owner is None or item.get("owner") == owner)
        and (status is None or item.get("status") == status)
    ], key=lambda item: item.get("updated_at", ""))


def _compatible(stored, current):
    if not stored or not current:
        return True
    if stored.get("project_id") and current.get("project_id"):
        return stored["project_id"] == current["project_id"]
    return True


def match_frontiers(problem, owner="automation", environment=None, limit=5):
    """Return active warnings ranked by cheap lexical overlap and applicability."""
    problem = _text(problem, "problem")
    limit = max(1, min(int(limit), 20))
    current = _environment(environment)
    query = query_terms(problem)
    matches = []
    for item in list_frontiers(owner=owner):
        if item.get("status") not in {"active", "candidate"}:
            continue
        stored_environment = item.get("environment") or {}
        if not _compatible(stored_environment, current):
            continue
        terms = query_terms(" ".join(
            item.get(key, "") for key in ("trigger", "risk", "warning")
        ) + " " + " ".join(item.get("counterexamples", [])))
        overlap = len(query & terms)
        if overlap == 0:
            continue
        matches.append({
            "id": item["id"],
            "trigger": item["trigger"],
            "risk": item["risk"],
            "warning": item["warning"],
            "verification": item["verification"],
            "counterexamples": item.get("counterexamples", []),
            "overlap": overlap,
            "status": item.get("status"),
        })
    return sorted(matches, key=lambda item: (-item["overlap"], item["id"]))[:limit]


def update_frontier(frontier_id, status, owner="automation", reason=None):
    if status not in STATUSES:
        raise ValueError("status must be candidate, active, stale, or rejected.")
    owner = _text(owner, "owner")
    item = next((row for row in _read() if row.get("id") == frontier_id), None)
    if item is None:
        raise ValueError(f"Failure frontier item was not found: {frontier_id}")
    if item.get("owner") != owner:
        raise ValueError("Failure frontier item is not owned by this agent.")
    item = dict(item)
    item["status"] = status
    if reason is not None:
        item["status_reason"] = _text(reason, "reason")
    return _append(item)


def feedback_frontier(frontier_id, outcome, owner="automation", reason=None):
    if outcome not in OUTCOMES:
        raise ValueError("outcome must be helpful, ignored, misleading, or harmful.")
    owner = _text(owner, "owner")
    item = next((row for row in _read() if row.get("id") == frontier_id), None)
    if item is None:
        raise ValueError(f"Failure frontier item was not found: {frontier_id}")
    if item.get("owner") != owner:
        raise ValueError("Failure frontier item is not owned by this agent.")
    updated = dict(item)
    feedback = list(updated.get("feedback", []))
    feedback.append({"outcome": outcome, "reason": reason or "", "at": utc_now()})
    updated["feedback"] = feedback[-20:]
    if outcome == "harmful":
        updated["status"] = "stale"
    elif outcome == "misleading" and updated.get("status") == "active":
        updated["status"] = "candidate"
    return _append(updated)


def restore_frontiers(frontiers):
    """Merge frontier manifests while preserving IDs and feedback history."""
    existing = {item.get("id") for item in _read()}
    merged = 0
    for frontier in frontiers or []:
        if not isinstance(frontier, dict) or not frontier.get("id") or frontier["id"] in existing:
            continue
        _append(dict(frontier))
        existing.add(frontier["id"])
        merged += 1
    return merged
