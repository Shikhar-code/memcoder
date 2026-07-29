"""Lifecycle and environment-applicability policy for trusted guidance."""

import hashlib
import json

from memory.records import VALID_RECORD_STATES, revise_record


RETRIEVAL_ELIGIBLE_STATES = {"trusted"}


def normalize_environment(environment):
    """Create a compact, deterministic fingerprint from host-supplied context."""
    if environment is None:
        return None
    if not isinstance(environment, dict):
        raise ValueError("environment must be an object when provided.")

    project_id = environment.get("project_id")
    if project_id is not None and (not isinstance(project_id, str) or not project_id.strip()):
        raise ValueError("environment.project_id must be a non-empty string when provided.")

    # The host controls the context it considers relevant: repository identity,
    # revision, dependencies, configuration, or a task-family fingerprint.
    compatibility = environment.get("compatibility")
    if compatibility is not None and not isinstance(compatibility, dict):
        raise ValueError("environment.compatibility must be an object when provided.")
    # Hosts may provide only the dimensions that actually determine safe
    # transfer (for example language/runtime/framework), avoiding false stale
    # warnings from unrelated environment details.
    fingerprint_basis = {
        "project_id": project_id.strip() if isinstance(project_id, str) else "",
        "compatibility": compatibility if compatibility is not None else environment,
    }
    try:
        canonical = json.dumps(fingerprint_basis, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError) as error:
        raise ValueError("environment must contain JSON-serializable values.") from error
    return {
        "project_id": project_id.strip() if isinstance(project_id, str) else "",
        "fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "compatibility_keys": sorted(compatibility) if compatibility is not None else [],
    }


def attach_environment(memory, environment):
    descriptor = normalize_environment(environment)
    if descriptor is not None:
        # Keep Chroma metadata scalar-only while SQLite retains the same record.
        memory["environment"] = json.dumps(descriptor, sort_keys=True)
    return memory


def _stored_environment(memory):
    value = memory.get("environment")
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value or "")
    except (TypeError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def applicability(memory, current_environment=None):
    """Describe whether a record may transfer into the host's current context."""
    stored = _stored_environment(memory)
    current = normalize_environment(current_environment)
    if not stored or not current:
        return {"status": "unknown", "penalty": 0.0}
    if stored.get("project_id") and current.get("project_id"):
        if stored["project_id"] != current["project_id"]:
            return {"status": "incompatible", "penalty": 1.0}
    if stored.get("fingerprint") == current.get("fingerprint"):
        return {"status": "match", "penalty": 0.0}
    return {"status": "changed", "penalty": 0.15}


def retrieval_eligible(memory, current_environment=None):
    """Return whether automatic guidance may use this record and why."""
    state = memory.get("record_state", "trusted")
    if state not in RETRIEVAL_ELIGIBLE_STATES:
        return False, {"status": "excluded_state", "record_state": state, "penalty": 1.0}
    assessment = applicability(memory, current_environment)
    if assessment["status"] == "incompatible":
        return False, assessment
    return True, assessment


def set_record_validity(record_id, state, owner=None, reason=None, environment=None):
    """Update a durable record's lifecycle state and immediately sync its index."""
    if state not in VALID_RECORD_STATES:
        raise ValueError("state must be a supported lifecycle state.")

    from memory.record_store import get_record, save_record

    memory = get_record(record_id)
    if memory is None:
        raise ValueError(f"Memory record was not found: {record_id}")
    if owner is not None and memory.get("owner") != owner:
        raise ValueError("Memory record is not owned by this agent.")

    memory["record_state"] = state
    if reason is not None:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string when provided.")
        memory["validity_reason"] = reason.strip()
    attach_environment(memory, environment)
    revise_record(memory)
    save_record(memory)

    from memory.index_sync import sync_record
    sync_record(memory)
    return memory
