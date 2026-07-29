"""Conservative, evidence-preserving retention and consolidation workflow."""

import hashlib
import json

from memory.record_store import get_record, list_records


RETENTION_SCHEMA_VERSION = 1


def _canonical(records):
    """Prefer an active, most-revised record while retaining every original."""
    return sorted(
        records,
        key=lambda record: (
            record.get("record_state") == "trusted",
            int(record.get("revision", 1)),
            record.get("updated_at", ""),
            record.get("record_id", ""),
        ),
        reverse=True,
    )[0]


def retention_preview(owner=None, environment=None):
    """Return deterministic, exact-duplicate actions without mutating storage."""
    groups = {}
    archived = []
    review_candidates = []
    from memory.validity import applicability
    for record in list_records():
        if owner is not None and record.get("owner") != owner:
            continue
        if record.get("record_state") in {"superseded", "deprecated"}:
            archived.append(record["record_id"])
            continue
        assessment = applicability(record, environment)
        if record.get("record_state") == "trusted" and assessment["status"] == "changed":
            review_candidates.append({
                "action": "review_environment_changed",
                "record_id": record["record_id"],
                "owner": record.get("owner"),
                "reason": "The current project fingerprint differs from the verified environment.",
            })
        groups.setdefault((record.get("owner"), record.get("content_hash")), []).append(record)

    actions = []
    for (_, _), records in groups.items():
        if len(records) < 2:
            continue
        canonical = _canonical(records)
        for record in records:
            if record["record_id"] == canonical["record_id"]:
                continue
            actions.append({
                "action": "supersede_exact_duplicate",
                "canonical_id": canonical["record_id"],
                "target_id": record["record_id"],
                "owner": record.get("owner"),
                "reason": "Exact duplicate content; preserve history and prefer the canonical record.",
                "content_hash": record.get("content_hash"),
            })

    canonical_json = json.dumps(actions, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": RETENTION_SCHEMA_VERSION,
        "owner": owner,
        "plan_id": "retention_" + hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()[:20],
        "actions": actions,
        "review_candidates": review_candidates,
        "already_archived": archived,
        "safe_to_apply": bool(actions),
        "guarantees": [
            "Only exact content duplicates are proposed.",
            "Applying a plan never deletes records or provenance.",
            "The duplicate is marked superseded and linked to its canonical record.",
            "Environment-drifted records are review candidates only and are never changed automatically.",
        ],
    }


def apply_retention_preview(preview, owner=None):
    """Apply a reviewed preview by state transition only; never delete records."""
    if not isinstance(preview, dict) or preview.get("schema_version") != RETENTION_SCHEMA_VERSION:
        raise ValueError("retention preview has an unsupported schema version.")
    actions = preview.get("actions")
    if not isinstance(actions, list):
        raise ValueError("retention preview actions must be a list.")

    applied = []
    for action in actions:
        if not isinstance(action, dict) or action.get("action") != "supersede_exact_duplicate":
            raise ValueError("retention preview contains an unsupported action.")
        canonical = get_record(action.get("canonical_id", ""))
        target = get_record(action.get("target_id", ""))
        if canonical is None or target is None:
            raise ValueError("retention action references a record that no longer exists.")
        expected_owner = owner if owner is not None else action.get("owner")
        if canonical.get("owner") != expected_owner or target.get("owner") != expected_owner:
            raise ValueError("retention action crosses an owner boundary.")
        if canonical.get("content_hash") != target.get("content_hash"):
            raise ValueError("retention action is no longer an exact duplicate.")
        if target.get("record_state") != "trusted":
            continue

        from memory.provenance import link
        from memory.validity import set_record_validity

        set_record_validity(
            target["record_id"],
            "superseded",
            owner=expected_owner,
            reason=action.get("reason"),
        )
        link(canonical["record_id"], target["record_id"], "supersedes", expected_owner)
        applied.append(target["record_id"])

    return {
        "plan_id": preview.get("plan_id", ""),
        "applied": applied,
        "deleted": [],
        "mode": "state_transition_only",
    }
