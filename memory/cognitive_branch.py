"""Provider-free, reversible branch-local cognition and proof gates."""

import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

from memory.records import utc_now
from memory.validity import normalize_environment


STATUSES = {"open", "merged", "rolled_back"}


def _path():
    configured = os.environ.get("MEMCODER_COGNITIVE_BRANCH_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_cognitive_branches.jsonl"


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


def _branch(branch_id):
    item = next((row for row in _read() if row.get("id") == branch_id), None)
    if item is None:
        raise ValueError(f"Cognitive branch was not found: {branch_id}")
    return item


def _owned(branch, owner):
    if owner is not None and branch.get("owner") != owner:
        raise ValueError("Cognitive branch is not owned by this agent.")


def create_branch(name, owner="automation", project_id=None, base_environment=None, base_ref=None):
    name = _text(name, "name")
    owner = _text(owner, "owner")
    if project_id is not None:
        project_id = _text(project_id, "project_id")
    environment = normalize_environment(base_environment) if base_environment is not None else None
    branch_id = "cbranch_" + hashlib.sha256(
        f"{owner}:{name}:{uuid4().hex}".encode("utf-8")
    ).hexdigest()[:20]
    return _append({
        "schema_version": 1,
        "id": branch_id,
        "name": name,
        "owner": owner,
        "project_id": project_id or "",
        "base_environment": environment or {},
        "base_ref": base_ref or "",
        "status": "open",
        "changes": [],
        "proof_obligations": [],
        "created_at": utc_now(),
    })


def list_branches(owner=None, status=None):
    if status is not None and status not in STATUSES:
        raise ValueError("status must be open, merged, or rolled_back.")
    return sorted([
        branch for branch in _read()
        if (owner is None or branch.get("owner") == owner)
        and (status is None or branch.get("status") == status)
    ], key=lambda branch: branch.get("created_at", ""))


def record_change(branch_id, kind, key, before=None, after=None, owner="automation", memory_ids=None):
    branch = _branch(branch_id)
    _owned(branch, owner)
    if branch.get("status") != "open":
        raise ValueError("Only an open cognitive branch can change.")
    kind, key = _text(kind, "kind"), _text(key, "key")
    changes = list(branch.get("changes", []))
    conflict = any(
        change.get("key") == key and change.get("after") != after
        for change in changes
    )
    changes.append({
        "id": "change_" + uuid4().hex[:16],
        "kind": kind,
        "key": key,
        "before": before,
        "after": after,
        "memory_ids": memory_ids if isinstance(memory_ids, list) else [],
        "conflict": conflict,
        "created_at": utc_now(),
    })
    updated = dict(branch)
    updated["changes"] = changes
    return _append(updated)


def add_proof_obligation(branch_id, name, kind="test", command=None, owner="automation"):
    branch = _branch(branch_id)
    _owned(branch, owner)
    if branch.get("status") != "open":
        raise ValueError("Only an open cognitive branch can add proof obligations.")
    obligation = {
        "id": "proof_" + uuid4().hex[:16],
        "name": _text(name, "name"),
        "kind": _text(kind, "kind"),
        "command": command or "",
        "status": "pending",
        "evidence": None,
        "created_at": utc_now(),
    }
    updated = dict(branch)
    updated["proof_obligations"] = [*branch.get("proof_obligations", []), obligation]
    return _append(updated)


def complete_proof_obligation(branch_id, obligation_id, passed, evidence, owner="automation"):
    branch = _branch(branch_id)
    _owned(branch, owner)
    if branch.get("status") != "open":
        raise ValueError("Only an open cognitive branch can receive proof.")
    if not isinstance(passed, bool):
        raise ValueError("passed must be a boolean.")
    if evidence is None or (isinstance(evidence, str) and not evidence.strip()):
        raise ValueError("evidence is required.")
    obligations = list(branch.get("proof_obligations", []))
    found = False
    for index, obligation in enumerate(obligations):
        if obligation.get("id") == obligation_id:
            obligation = dict(obligation)
            obligation["status"] = "passed" if passed else "failed"
            obligation["evidence"] = evidence
            obligation["verified_at"] = utc_now()
            obligations[index] = obligation
            found = True
            break
    if not found:
        raise ValueError(f"Proof obligation was not found: {obligation_id}")
    updated = dict(branch)
    updated["proof_obligations"] = obligations
    return _append(updated)


def cognitive_diff(branch_id, target_branch_id=None, owner="automation"):
    branch = _branch(branch_id)
    _owned(branch, owner)
    target = _branch(target_branch_id) if target_branch_id else None
    if target:
        _owned(target, owner)
    target_changes = {item.get("key"): item for item in (target or {}).get("changes", [])}
    changes = []
    conflicts = []
    for item in branch.get("changes", []):
        other = target_changes.get(item.get("key"))
        entry = {"key": item.get("key"), "kind": item.get("kind"), "before": item.get("before"), "after": item.get("after")}
        if other and other.get("after") != item.get("after"):
            entry["conflict"] = True
            conflicts.append(entry)
        else:
            entry["conflict"] = bool(item.get("conflict"))
        changes.append(entry)
    return {
        "branch_id": branch_id,
        "target_branch_id": target_branch_id,
        "changes": changes,
        "conflicts": conflicts,
        "change_count": len(changes),
        "proof_obligations": branch.get("proof_obligations", []),
    }


def merge_branch(branch_id, owner="automation", target_branch_id=None, environment=None, apply=False):
    branch = _branch(branch_id)
    _owned(branch, owner)
    if branch.get("status") != "open":
        return {"branch_id": branch_id, "merge_allowed": False, "reason": "branch is not open"}
    diff = cognitive_diff(branch_id, target_branch_id, owner=owner)
    obligations = branch.get("proof_obligations", [])
    failed = [item["id"] for item in obligations if item.get("status") != "passed"]
    base = branch.get("base_environment") or {}
    current = normalize_environment(environment) if environment is not None else None
    drift = bool(base and current and base.get("fingerprint") != current.get("fingerprint"))
    reasons = []
    if not obligations:
        reasons.append("no proof obligations were attached")
    if failed:
        reasons.append("proof obligations are incomplete or failed")
    if diff["conflicts"]:
        reasons.append("cognitive diff contains conflicts")
    if drift:
        reasons.append("branch environment changed; revalidation is required")
    allowed = not reasons
    result = {"branch_id": branch_id, "merge_allowed": allowed, "reasons": reasons, "diff": diff}
    if allowed and apply:
        updated = dict(branch)
        updated["status"] = "merged"
        updated["merged_at"] = utc_now()
        updated["merged_change_count"] = len(diff["changes"])
        _append(updated)
        result["status"] = "merged"
    else:
        result["status"] = branch.get("status")
    return result


def rollback_branch(branch_id, owner="automation", reason=None):
    branch = _branch(branch_id)
    _owned(branch, owner)
    updated = dict(branch)
    updated["status"] = "rolled_back"
    updated["rollback_reason"] = reason or "Reversible cognitive branch rollback."
    updated["rolled_back_at"] = utc_now()
    return _append(updated)


def restore_branches(branches):
    """Merge branch manifests while preserving IDs and audit state."""
    existing = {item.get("id") for item in _read()}
    merged = 0
    for branch in branches or []:
        if not isinstance(branch, dict) or not branch.get("id") or branch["id"] in existing:
            continue
        _append(dict(branch))
        existing.add(branch["id"])
        merged += 1
    return merged
