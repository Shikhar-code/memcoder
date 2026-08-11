"""Provider-free lifecycle attention, risk, verification, and token accounting."""

import hashlib
import json
import os
import re
from pathlib import Path

from memory.records import utc_now


LIFECYCLE_EVENTS = {
    "task_started", "context_changed", "before_plan", "before_edit", "before_tool",
    "verification_started", "verification_finished", "task_completed", "task_failed",
}
INTERVENTION_EVENTS = {"task_started", "context_changed", "before_plan", "before_edit", "before_tool"}
HIGH_RISK_PATTERNS = {
    "destructive": r"\b(delete|remove|drop|truncate|reset --hard|force push|overwrite)\b",
    "dependency": r"\b(install|upgrade|dependency|package|lockfile)\b",
    "migration": r"\b(migrate|migration|schema|database|index)\b",
    "release": r"\b(release|publish|deploy|upload|production)\b",
    "security": r"\b(secret|token|credential|permission|auth|security)\b",
}


def _path():
    configured = os.environ.get("MEMCODER_AUTOPILOT_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_autopilot.jsonl"


def _events():
    path = _path()
    if not path.exists():
        return []
    loaded = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                loaded.append(event)
    return loaded


def _append(event):
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    stored = {**event, "timestamp": event.get("timestamp") or utc_now()}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(stored, sort_keys=True, ensure_ascii=False) + "\n")
    return stored


def _fingerprint(problem, context=None, action=None):
    value = json.dumps(
        {"problem": problem, "context": context or {}, "action": action or ""},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def _latest_control(owner):
    controls = [
        event for event in _events()
        if event.get("kind") == "control" and event.get("owner") == owner
    ]
    return controls[-1].get("state", "running") if controls else "running"


def failure_radar(problem, action=None):
    """Return a cheap preflight warning only for materially risky actions."""
    text = f"{problem or ''} {action or ''}".lower()
    risks = [name for name, pattern in HIGH_RISK_PATTERNS.items() if re.search(pattern, text)]
    if not risks:
        return {"risk": "normal", "mechanisms": [], "applicability": "none", "cheapest_check": None}
    checks = {
        "destructive": "Preview the exact targets and confirm rollback before execution.",
        "dependency": "Inspect the existing dependency declaration and run its focused install/build check.",
        "migration": "Back up current data and dry-run the migration against a disposable copy.",
        "release": "Build and validate the exact release artifact before publishing.",
        "security": "Confirm secrets stay out of logs and run the narrow security/auth check.",
    }
    return {
        "risk": "high",
        "mechanisms": risks,
        "applicability": "The proposed action matches a high-cost failure mechanism.",
        "cheapest_check": checks[risks[0]],
    }


def verification_plan(problem, environment=None, radar=None):
    """Choose the smallest native proof proportional to current risk."""
    environment = environment or {}
    available = [str(item) for item in environment.get("available_checks", []) if str(item).strip()]
    risk = (radar or {}).get("risk", "normal")
    if available:
        checks = available[:2 if risk == "high" else 1]
        source = "host_native"
    else:
        checks = ["Run the narrowest current-project test, assertion, build, or documented review."]
        source = "fallback"
    return {
        "risk": risk,
        "checks": checks,
        "source": source,
        "requirement": "A command pass is evidence only when it exercises the requested behavior.",
    }


def begin_event(event, task_id, owner, problem, context=None, action=None, environment=None):
    """Decide whether one lifecycle boundary warrants cognition."""
    if event not in LIFECYCLE_EVENTS:
        raise ValueError(f"Unsupported lifecycle event: {event}")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id must be a non-empty string.")
    state = _latest_control(owner)
    fingerprint = _fingerprint(problem, context=context, action=action)
    prior = [
        item for item in _events()
        if item.get("kind") == "lifecycle"
        and item.get("owner") == owner
        and item.get("task_id") == task_id
        and item.get("fingerprint") == fingerprint
        and item.get("intervened")
    ]
    radar = failure_radar(problem, action=action)
    should_intervene = (
        state == "running"
        and event in INTERVENTION_EVENTS
        and (not prior or event == "context_changed")
    )
    return {
        "event": event,
        "task_id": task_id,
        "owner": owner,
        "state": state,
        "fingerprint": fingerprint,
        "should_intervene": should_intervene,
        "deduplicated": bool(prior) and not should_intervene,
        "radar": radar,
        "verification_plan": verification_plan(problem, environment=environment, radar=radar),
    }


def finish_event(decision, intervention=None, capture=None, token_budget=450):
    """Persist a compact lifecycle receipt and token-dividend estimate."""
    transfer = (intervention or {}).get("transfer_delta") or {}
    verified_risks = [risk for risk in transfer.get("risks", []) if risk]
    if verified_risks:
        decision["radar"] = {
            "risk": "high",
            "mechanisms": list(dict.fromkeys(
                decision["radar"].get("mechanisms", []) + verified_risks
            )),
            "applicability": "Retrieved verified evidence names a failure mechanism for this task.",
            "cheapest_check": (transfer.get("required_verification") or [
                decision["radar"].get("cheapest_check")
            ])[0],
        }
    mode = (intervention or {}).get("intervention", {}).get("mode", "none")
    budget = (intervention or {}).get("budget", {})
    injected = int(budget.get("estimated_tokens", 0) or 0)
    avoided = max(0, int(token_budget) - injected) if intervention else 0
    stored = _append({
        "kind": "lifecycle",
        **decision,
        "intervened": intervention is not None,
        "intervention_id": (intervention or {}).get("receipt", {}).get("id"),
        "mode": mode,
        "capture": capture,
        "ledger": {
            "injected_tokens": injected,
            "expansions": 0,
            "estimated_context_tokens_avoided": avoided,
            "net_token_dividend": avoided - injected,
        },
    })
    return {
        "available": True,
        "fail_open": False,
        "event": decision["event"],
        "task_id": decision["task_id"],
        "attention": {
            "state": decision["state"],
            "intervened": intervention is not None,
            "deduplicated": decision["deduplicated"],
            "mode": mode,
        },
        "radar": decision["radar"],
        "verification_plan": decision["verification_plan"],
        "cognition": intervention,
        "capture": capture,
        "ledger": stored["ledger"],
    }


def token_ledger(owner, task_id=None):
    rows = [
        event for event in _events()
        if event.get("kind") == "lifecycle" and event.get("owner") == owner
        and (task_id is None or event.get("task_id") == task_id)
    ]
    totals = {
        "events": len(rows),
        "interventions": sum(bool(row.get("intervened")) for row in rows),
        "injected_tokens": sum(row.get("ledger", {}).get("injected_tokens", 0) for row in rows),
        "estimated_context_tokens_avoided": sum(
            row.get("ledger", {}).get("estimated_context_tokens_avoided", 0) for row in rows
        ),
        "net_token_dividend": sum(row.get("ledger", {}).get("net_token_dividend", 0) for row in rows),
    }
    return {"owner": owner, "task_id": task_id, "totals": totals, "events": rows[-20:]}


def control(action, owner, task_id=None):
    """Pause, resume, inspect, or request rollback without hiding state changes."""
    if action == "pause":
        _append({"kind": "control", "owner": owner, "state": "paused"})
        return {"state": "paused"}
    if action == "resume":
        _append({"kind": "control", "owner": owner, "state": "running"})
        return {"state": "running"}
    if action in {"status", "inspect"}:
        result = {"state": _latest_control(owner)}
        if action == "inspect":
            result["ledger"] = token_ledger(owner, task_id=task_id)
        return result
    if action == "rollback":
        captures = [
            event.get("capture") for event in _events()
            if event.get("kind") == "lifecycle" and event.get("owner") == owner
            and (task_id is None or event.get("task_id") == task_id)
            and isinstance(event.get("capture"), dict)
        ]
        record_ids = []
        for capture in captures:
            record_ids.extend(capture.get("record_ids", []))
        return {"state": _latest_control(owner), "rollback_record_ids": list(dict.fromkeys(record_ids))}
    raise ValueError("action must be pause, resume, status, inspect, or rollback.")
