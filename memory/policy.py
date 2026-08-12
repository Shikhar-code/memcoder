"""Local admission and export policy for MemCoder cognition."""

import fnmatch
import json
import os
import re
from pathlib import Path


POLICY_SCHEMA_VERSION = 1
SECRET_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|secret|password|token|access[_-]?key|private[_-]?key)\b\s*([:=])\s*(?!\[+\s*\])[\"']?[^\s,\"']+"
)


class PolicyDenied(ValueError):
    """Raised when a memory write violates the local admission policy."""


def policy_path():
    configured = os.environ.get("MEMCODER_POLICY_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_policy.json"


def default_policy():
    return {
        "schema_version": POLICY_SCHEMA_VERSION,
        "admission": {
            "deny": ["**/.env", "**/.env.*", "**/secrets/**", "**/*.key", "**/*.pem"],
            "redact_secrets": True,
        },
        # Preserve Beta 2 retrieval compatibility; hosts can disable this explicitly.
        "retrieval": {"default_scope": "project", "allow_shared": True},
        "retention": {"keep_revisions": True, "review_after_days": 90},
        "export": {"require_approval": True, "allow_shared": False},
    }


def normalize_policy(policy):
    if policy is None:
        policy = default_policy()
    if not isinstance(policy, dict):
        raise ValueError("policy must be an object.")
    normalized = default_policy()
    for section in ("admission", "retrieval", "retention", "export"):
        supplied = policy.get(section)
        if supplied is not None and not isinstance(supplied, dict):
            raise ValueError(f"policy.{section} must be an object.")
        if isinstance(supplied, dict):
            normalized[section].update(supplied)
    deny = normalized["admission"].get("deny", [])
    if not isinstance(deny, list) or not all(isinstance(item, str) and item.strip() for item in deny):
        raise ValueError("policy.admission.deny must be a list of non-empty strings.")
    normalized["admission"]["deny"] = [item.strip().replace("\\", "/") for item in deny]
    normalized["schema_version"] = POLICY_SCHEMA_VERSION
    return normalized


def load_policy(path=None):
    path = Path(path or policy_path())
    if not path.exists():
        return default_policy()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read policy: {error}") from error
    return normalize_policy(value)


def save_policy(policy, path=None):
    path = Path(path or policy_path())
    normalized = normalize_policy(policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"path": str(path), "schema_version": POLICY_SCHEMA_VERSION}


def _matches(path, pattern):
    value = str(path or "").replace("\\", "/").lower()
    pattern = pattern.lower()
    basename = value.rsplit("/", 1)[-1]
    suffix_pattern = pattern[3:] if pattern.startswith("**/") else pattern
    return (
        fnmatch.fnmatchcase(value, pattern)
        or fnmatch.fnmatchcase(basename, pattern)
        or fnmatch.fnmatchcase(value, suffix_pattern)
        or fnmatch.fnmatchcase(basename, suffix_pattern)
    )


def redact_text(value):
    return SECRET_PATTERN.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", str(value or ""))


def evaluate_admission(*, files=None, text=None, owner=None, project_id=None, policy=None):
    """Return an explainable admission decision without writing anything."""
    policy = normalize_policy(policy or load_policy())
    files = [str(item) for item in (files or [])]
    text = [str(item) for item in (text or []) if item is not None]
    matched = []
    for file_path in files:
        for pattern in policy["admission"]["deny"]:
            if _matches(file_path, pattern):
                matched.append({"kind": "path", "value": file_path, "rule": pattern})
    secret_hits = [item.group(0) for value in text for item in SECRET_PATTERN.finditer(value)]
    if secret_hits:
        matched.append({"kind": "secret", "rule": "secret_assignment", "count": len(secret_hits)})
    allowed = not matched
    return {
        "allowed": allowed,
        "action": "admit" if allowed else "deny",
        "owner": owner,
        "project_id": project_id,
        "matched_rules": matched,
        "policy": policy,
        "explanation": "No admission rule matched." if allowed else "Admission blocked by the Memory Firewall.",
    }


def evaluate_retrieval(*, owner=None, project_id=None, include_shared=False, policy=None):
    """Return the scope a host may use before it performs retrieval."""
    policy = normalize_policy(policy or load_policy())
    retrieval = policy["retrieval"]
    requested_shared = bool(include_shared)
    shared_allowed = bool(retrieval.get("allow_shared", False))
    if requested_shared and not shared_allowed:
        return {
            "allowed": False,
            "scope": retrieval.get("default_scope", "project"),
            "owner": owner,
            "project_id": project_id,
            "reason": "Shared retrieval is disabled by local policy.",
            "policy": policy,
        }
    return {
        "allowed": True,
        "scope": "shared" if requested_shared else retrieval.get("default_scope", "project"),
        "owner": owner,
        "project_id": project_id,
        "reason": "Retrieval scope is allowed by local policy.",
        "policy": policy,
    }


def evaluate_export(*, owner=None, project_id=None, include_shared=False, approved=False, policy=None):
    """Check export scope without reading or writing any files."""
    policy = normalize_policy(policy or load_policy())
    export = policy["export"]
    if bool(include_shared) and not bool(export.get("allow_shared", False)):
        return {"allowed": False, "reason": "Shared export is disabled by local policy.", "policy": policy}
    if bool(export.get("require_approval", True)) and not approved:
        return {"allowed": False, "reason": "Export requires explicit approval.", "policy": policy}
    return {
        "allowed": True,
        "owner": owner,
        "project_id": project_id,
        "reason": "Export scope is allowed by local policy.",
        "policy": policy,
    }


def policy_status(path=None):
    path = Path(path or policy_path())
    return {
        "path": str(path),
        "exists": path.exists(),
        "policy": load_policy(path),
    }
