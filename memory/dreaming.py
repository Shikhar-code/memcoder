"""Automatic, local Dreaming that produces evidence-gated candidates.

Dreaming is deliberately provider-free.  It may propose a pattern from trusted
episodes, but it cannot affect retrieval until a host supplies sandbox proof.
"""

import hashlib
import json
import os
import re
from pathlib import Path

from memory.records import record_id, utc_now
from memory.record_store import list_records


DREAM_SCHEMA_VERSION = 1
_STOP_WORDS = {
    "and", "are", "before", "being", "from", "into", "must", "only",
    "that", "the", "this", "with", "when", "where", "while", "your",
}


def _path():
    configured = os.environ.get("MEMCODER_DREAM_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_dreams.jsonl"


def _read():
    path = _path()
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                rows.append(value)
    return rows


def _append(value):
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {**value, "timestamp": value.get("timestamp") or utc_now()}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    return row


def _terms(value):
    return {
        token for token in re.findall(r"[A-Za-z0-9_]{3,}", str(value or "").lower())
        if token not in _STOP_WORDS
    }


def _json_object(value):
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value or "")
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _qa_approved(record):
    return _json_object(record.get("verification")).get("qa_verdict") == "approved"


def _trusted_experiences(owner, environment, records=None):
    from memory.validity import retrieval_eligible

    eligible_records = []
    for record in records if records is not None else list_records():
        if record.get("type") != "experience" or record.get("owner") != owner:
            continue
        if record.get("record_state", "trusted") != "trusted" or not _qa_approved(record):
            continue
        eligible, _ = retrieval_eligible(record, current_environment=environment)
        if eligible:
            eligible_records.append(record)
    return eligible_records


def _latest_candidate(candidate_id, owner):
    rows = [
        row for row in _read()
        if row.get("kind") == "dream_candidate"
        and row.get("candidate_id") == candidate_id
        and row.get("owner") == owner
    ]
    return rows[-1] if rows else None


def list_candidates(owner="human", status=None):
    """Return the latest owner-scoped candidate state without changing it."""
    latest = {}
    for row in _read():
        if row.get("kind") != "dream_candidate" or row.get("owner") != owner:
            continue
        latest[row.get("candidate_id")] = row
    values = list(latest.values())
    if status is not None:
        values = [row for row in values if row.get("status") == status]
    return values


def snapshot_candidates():
    """Return latest candidate states for portable backups."""
    latest = {}
    for row in _read():
        if row.get("kind") != "dream_candidate" or not row.get("candidate_id"):
            continue
        latest[(row.get("owner"), row["candidate_id"])] = row
    return list(latest.values())


def restore_candidates(candidates):
    """Merge candidate states without replacing newer local history."""
    if not isinstance(candidates, list):
        raise ValueError("dream_candidates must be a list.")
    existing = {
        (row.get("owner"), row.get("candidate_id"))
        for row in snapshot_candidates()
    }
    restored = 0
    for candidate in candidates:
        if not isinstance(candidate, dict) or not candidate.get("candidate_id"):
            continue
        key = (candidate.get("owner"), candidate["candidate_id"])
        if key in existing:
            continue
        _append(candidate)
        existing.add(key)
        restored += 1
    return restored


def _candidate_for(first, second, all_records=None):
    first_terms = _terms(first.get("task"))
    second_terms = _terms(second.get("task"))
    overlap = sorted(first_terms & second_terms)
    if len(overlap) < 2:
        return None
    source_ids = sorted({record_id(first), record_id(second)})
    signature = "|".join(overlap[:8])
    candidate_id = "dream_" + hashlib.sha256(
        (signature + "|" + "|".join(source_ids)).encode("utf-8")
    ).hexdigest()[:20]
    candidate = {
        "schema_version": DREAM_SCHEMA_VERSION,
        "kind": "dream_candidate",
        "candidate_id": candidate_id,
        "owner": first.get("owner", "human"),
        "status": "candidate",
        "pattern_terms": overlap[:8],
        "insight": (
            "Verified tasks share a decision pattern around "
            + ", ".join(overlap[:6])
            + ". Re-check task-specific assumptions and repeat proof before reuse."
        ),
        "source_experience_ids": source_ids,
        "support_count": len(source_ids),
        "counterexamples": [],
        "sandbox": {"status": "pending", "checks": []},
        "created_at": utc_now(),
    }
    if all_records:
        candidate["counterexamples"] = sorted({
            record_id(record) for record in all_records
            if record.get("type") == "experience"
            and record.get("record_state", "trusted") != "trusted"
            and set(candidate["pattern_terms"]) <= _terms(record.get("task"))
        })
    return candidate


def run_dream(owner="human", environment=None, max_candidates=5):
    """Automatically propose compact candidates from trusted verified episodes."""
    if not isinstance(owner, str) or not owner.strip():
        raise ValueError("owner must be a non-empty string.")
    if not isinstance(max_candidates, int) or isinstance(max_candidates, bool) or max_candidates < 1:
        raise ValueError("max_candidates must be a positive integer.")
    all_records = list_records()
    episodes = _trusted_experiences(owner, environment, records=all_records)
    existing = {row.get("candidate_id") for row in list_candidates(owner)}
    created = []
    for index, first in enumerate(episodes):
        for second in episodes[index + 1:]:
            candidate = _candidate_for(first, second, all_records=all_records)
            if not candidate or candidate["candidate_id"] in existing:
                continue
            stored = _append(candidate)
            existing.add(candidate["candidate_id"])
            created.append(stored)
            if len(created) >= max_candidates:
                break
        if len(created) >= max_candidates:
            break
    return {
        "automatic": True,
        "owner": owner,
        "source_experiences": len(episodes),
        "created": created,
        "candidates": list_candidates(owner),
        "promotion_policy": "Sandbox evidence is required; trusted records are never changed silently.",
    }


def evaluate_candidate(candidate_id, checks, owner="human", auto_promote=True):
    """Record sandbox evidence and promote only an eligible candidate."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")
    if not isinstance(checks, list) or not checks:
        raise ValueError("checks must contain at least one sandbox check.")
    candidate = _latest_candidate(candidate_id, owner)
    if candidate is None:
        raise ValueError(f"Dream candidate was not found: {candidate_id}")
    if candidate.get("status") in {"promoted", "rolled_back", "rejected"}:
        raise ValueError("Dream candidate is no longer eligible for sandbox evaluation.")
    normalized = []
    for check in checks:
        if not isinstance(check, dict) or not str(check.get("name", "")).strip():
            raise ValueError("Each sandbox check needs a name and passed boolean.")
        if not isinstance(check.get("passed"), bool):
            raise ValueError("Each sandbox check needs a name and passed boolean.")
        if not str(check.get("evidence", "")).strip():
            raise ValueError("Each sandbox check needs inspectable evidence.")
        normalized.append({
            "name": str(check["name"]).strip(),
            "passed": check["passed"],
            "evidence": str(check["evidence"]).strip(),
        })
    passed = all(check["passed"] for check in normalized)
    updated = {
        **candidate,
        "status": "sandboxed" if passed else "rejected",
        "sandbox": {"status": "passed" if passed else "failed", "checks": normalized},
    }
    _append(updated)
    promoted = None
    if passed and auto_promote:
        promoted = promote_candidate(candidate_id, owner=owner)
    return {"candidate": updated, "promoted": promoted}


def promote_candidate(candidate_id, owner="human"):
    """Promote a sandbox-passed candidate into one reversible Principle."""
    candidate = _latest_candidate(candidate_id, owner)
    if candidate is None:
        raise ValueError(f"Dream candidate was not found: {candidate_id}")
    if candidate.get("sandbox", {}).get("status") != "passed":
        raise ValueError("Dream candidate requires passed sandbox evidence before promotion.")
    if candidate.get("counterexamples"):
        raise ValueError("Dream candidate has unresolved counterexamples.")

    from memory.capture import capture_memory
    from memory.provenance import link

    memory = capture_memory(
        task="Dreamed principle: " + candidate["insight"],
        files=["memcoder_dreaming"],
        summary="Automatically consolidated from verified experiences after sandbox checks.",
        solution=candidate["insight"],
        importance=6,
        memory_type="principle",
        owner=owner,
        source="dreaming",
        verification=json.dumps({
            "qa_verdict": "approved",
            "dream_candidate_id": candidate_id,
            "sandbox": candidate["sandbox"],
        }, sort_keys=True),
        metadata={
            "dream_candidate_id": candidate_id,
            "dream_supporting_experience_ids": json.dumps(
                candidate["source_experience_ids"], sort_keys=True
            ),
        },
    )
    promoted_id = record_id(memory)
    for source_id in candidate["source_experience_ids"]:
        try:
            link(source_id, promoted_id, "supports", owner, metadata={"dream_candidate_id": candidate_id})
        except ValueError:
            continue
    _append({
        **candidate,
        "status": "promoted",
        "promoted_record_id": promoted_id,
    })
    return {"candidate_id": candidate_id, "record_id": promoted_id, "status": "promoted"}


def rollback_candidate(candidate_id, owner="human"):
    """Deprecate any promoted record and mark the candidate rolled back."""
    candidate = _latest_candidate(candidate_id, owner)
    if candidate is None:
        raise ValueError(f"Dream candidate was not found: {candidate_id}")
    record_id_value = candidate.get("promoted_record_id")
    if record_id_value:
        from memory.validity import set_record_validity
        set_record_validity(
            record_id_value,
            "deprecated",
            owner=owner,
            reason="Dream candidate was rolled back by the owner.",
        )
    _append({
        **candidate,
        "status": "rolled_back",
        "rollback_record_id": record_id_value,
    })
    return {
        "candidate_id": candidate_id,
        "status": "rolled_back",
        "record_id": record_id_value,
    }
