"""Portable, checksummed cognition capsules for local handoff and backup."""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from memory.records import utc_now


CAPSULE_SCHEMA_VERSION = 1


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _owned(value, owner):
    if owner is None:
        return True
    return value.get("owner") in {owner, "shared"}


def _redact_record(record):
    from memory.policy import redact_text
    result = dict(record)
    for field in ("task", "summary", "solution", "verification"):
        if field in result:
            result[field] = redact_text(result[field])
    return result


def build_capsule(owner=None, project_id=None, policy=None):
    from memory.storage_ops import build_snapshot
    from memory.policy import load_policy
    snapshot = build_snapshot()
    active_policy = policy or load_policy()
    if owner is not None:
        records = [row for row in snapshot["records"] if _owned(row, owner)]
        ids = {row.get("record_id") for row in records}
        snapshot["records"] = records
        snapshot["provenance_edges"] = [
            row for row in snapshot["provenance_edges"]
            if _owned(row, owner) and (row.get("source_id") in ids or row.get("target_id") in ids)
        ]
        for field in ("dream_candidates", "failure_frontiers", "cognitive_branches"):
            snapshot[field] = [row for row in snapshot.get(field, []) if _owned(row, owner)]
    if active_policy.get("admission", {}).get("redact_secrets", True):
        snapshot["records"] = [_redact_record(record) for record in snapshot["records"]]
    project_state = None
    if project_id and owner:
        from memory.project_cortex import read_project_state
        project_state = read_project_state(project_id, owner)
    capsule_policy = dict(policy or {"import_requires_review": True})
    capsule_policy["redacted"] = bool(active_policy.get("admission", {}).get("redact_secrets", True))
    payload = {
        "kind": "memcoder_capsule",
        "schema_version": CAPSULE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "source_owner": owner,
        "project_id": project_id,
        "policy": capsule_policy,
        "snapshot": snapshot,
        "project_state": project_state,
    }
    payload["checksum"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return payload


def verify_capsule(capsule):
    if not isinstance(capsule, dict) or capsule.get("kind") != "memcoder_capsule":
        raise ValueError("capsule must be a MemCoder capsule.")
    if capsule.get("schema_version") != CAPSULE_SCHEMA_VERSION:
        raise ValueError("capsule has an unsupported schema version.")
    supplied = capsule.get("checksum")
    unsigned = {key: value for key, value in capsule.items() if key != "checksum"}
    expected = hashlib.sha256(_canonical(unsigned).encode("utf-8")).hexdigest()
    if supplied != expected:
        raise ValueError("capsule checksum is missing or invalid.")
    snapshot = capsule.get("snapshot")
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("records"), list):
        raise ValueError("capsule snapshot must contain records.")
    if capsule.get("project_state") is not None and not isinstance(capsule["project_state"], dict):
        raise ValueError("capsule project_state must be an object when provided.")
    return {"valid": True, "checksum": expected, "records": len(snapshot["records"]), "project_id": capsule.get("project_id")}


def write_capsule(output, owner=None, project_id=None, policy=None):
    path = Path(output)
    if path.suffix.lower() not in {".json", ".mcc"}:
        raise ValueError("capsule output must end in .json or .mcc")
    path.parent.mkdir(parents=True, exist_ok=True)
    capsule = build_capsule(owner=owner, project_id=project_id, policy=policy)
    path.write_text(json.dumps(capsule, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**verify_capsule(capsule), "path": str(path)}


def read_capsule(input_path):
    path = Path(input_path)
    try:
        capsule = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read capsule: {error}") from error
    verify_capsule(capsule)
    return capsule


def import_capsule(capsule, *, apply=False, owner=None, policy=None):
    from memory.policy import evaluate_admission
    verify_capsule(capsule)
    snapshot = capsule["snapshot"]
    blocked = []
    for record in snapshot.get("records", []):
        decision = evaluate_admission(
            files=record.get("files", []),
            text=[record.get("task"), record.get("summary"), record.get("solution"), record.get("verification")],
            owner=owner,
            policy=policy,
        )
        if not decision["allowed"]:
            blocked.append({"id": record.get("record_id"), "matched_rules": decision["matched_rules"]})
    result = {"valid": True, "dry_run": not apply, "records": len(snapshot.get("records", [])), "blocked": blocked}
    if blocked or not apply:
        return result
    from memory.storage_ops import restore_snapshot
    temp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    try:
        temp.write(json.dumps(snapshot, ensure_ascii=False))
        temp.close()
        result["restore"] = restore_snapshot(temp.name)
        project_state = capsule.get("project_state")
        if project_state:
            from memory.project_cortex import update_project_state
            target_owner = owner or capsule.get("source_owner") or "automation"
            result["project_state"] = update_project_state(
                project_state.get("project_id") or capsule.get("project_id") or "",
                target_owner,
                {
                    **project_state.get("state", {}),
                    "decisions": project_state.get("decisions", []),
                },
                environment=project_state.get("environment"),
            )
    finally:
        try:
            os.unlink(temp.name)
        except OSError:
            pass
    result["dry_run"] = False
    return result


def capsule_action(action, request):
    if action == "export":
        return write_capsule(request.get("output"), owner=request.get("owner"), project_id=request.get("project_id"), policy=request.get("policy"))
    if action in {"inspect", "verify"}:
        capsule = request.get("capsule") or read_capsule(request.get("input_path"))
        result = verify_capsule(capsule)
        if action == "inspect":
            result["source_owner"] = capsule.get("source_owner")
            result["policy"] = capsule.get("policy")
        return result
    if action == "import":
        capsule = request.get("capsule") or read_capsule(request.get("input_path"))
        return import_capsule(capsule, apply=bool(request.get("apply")), owner=request.get("owner"), policy=request.get("policy"))
    raise ValueError("capsule action must be export, inspect, verify, or import.")
