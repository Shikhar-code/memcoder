"""Append-only local storage for non-guidance audit records."""

import json
import os
from pathlib import Path

from memory.records import utc_now


def _audit_path():
    configured = os.environ.get("MEMCODER_AUDIT_PATH")
    if configured:
        return Path(configured)

    # Keep audit data beside the configured Chroma database during the staged
    # storage migration, without putting it in the guidance collection.
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_plan_outcomes.jsonl"


def append_plan_outcome(entry):
    path = _audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    stored = {**entry, "timestamp": entry.get("timestamp") or utc_now()}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(stored, sort_keys=True) + "\n")
    return stored


def plan_outcome_history(plan_id, agent_id):
    path = _audit_path()
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("plan_id") == plan_id and entry.get("owner") == agent_id:
                entries.append(entry)
    return sorted(entries, key=lambda entry: entry.get("timestamp", ""), reverse=True)


def outcomes_for_skill(skill_id, agent_id):
    """Return one owner's plan audits linked to a promoted Skill."""
    path = _audit_path()
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("owner") == agent_id and entry.get("applied_skill_id") == skill_id:
                entries.append(entry)
    return sorted(entries, key=lambda entry: entry.get("timestamp", ""), reverse=True)


def list_audit_entries():
    path = _audit_path()
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict):
                entries.append(entry)
    return entries


def merge_audit_entries(entries):
    """Append imported audit entries only when their durable IDs are new."""
    if not isinstance(entries, list):
        raise ValueError("audit entries must be a list.")
    existing_ids = {entry.get("id") for entry in list_audit_entries() if entry.get("id")}
    merged = 0
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("id") or entry["id"] in existing_ids:
            continue
        append_plan_outcome(entry)
        existing_ids.add(entry["id"])
        merged += 1
    return merged
