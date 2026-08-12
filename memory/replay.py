"""Deterministic comparison of captured cognition conditions."""

import hashlib
import json
import os
from pathlib import Path

from memory.records import utc_now


REPLAY_SCHEMA_VERSION = 1


def _path():
    configured = os.environ.get("MEMCODER_REPLAY_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_replays.jsonl"


def _case(value, index):
    if not isinstance(value, dict):
        raise ValueError("each replay case must be an object.")
    case_id = str(value.get("id") or f"case-{index + 1}").strip()
    label = str(value.get("label") or case_id).strip()
    memory_ids = value.get("memory_ids", [])
    if not isinstance(memory_ids, list):
        raise ValueError("replay case memory_ids must be a list.")
    outcome = value.get("outcome") if isinstance(value.get("outcome"), dict) else {}
    return {
        "id": case_id,
        "label": label,
        "strategy": str(value.get("strategy") or "unknown"),
        "memory_ids": [str(item) for item in memory_ids],
        "tokens": int(value.get("tokens", outcome.get("tokens", 0)) or 0),
        "rework": int(value.get("rework", outcome.get("rework", 0)) or 0),
        "passed": outcome.get("passed", value.get("passed")),
    }


def compare_cases(task, cases):
    if not isinstance(task, str) or not task.strip():
        raise ValueError("replay task must be a non-empty string.")
    if not isinstance(cases, list) or len(cases) < 2:
        raise ValueError("replay requires at least a baseline and one comparison case.")
    normalized = [_case(case, index) for index, case in enumerate(cases)]
    baseline = normalized[0]
    comparisons = []
    for candidate in normalized[1:]:
        baseline_ids, candidate_ids = set(baseline["memory_ids"]), set(candidate["memory_ids"])
        comparisons.append({
            "against": baseline["id"],
            "case": candidate["id"],
            "memory_added": sorted(candidate_ids - baseline_ids),
            "memory_removed": sorted(baseline_ids - candidate_ids),
            "token_delta": candidate["tokens"] - baseline["tokens"],
            "rework_delta": candidate["rework"] - baseline["rework"],
            "passed_delta": None if baseline["passed"] is None or candidate["passed"] is None else bool(candidate["passed"]) - bool(baseline["passed"]),
        })
    payload = {"schema_version": REPLAY_SCHEMA_VERSION, "task": task.strip(), "cases": normalized, "comparisons": comparisons}
    replay_id = "replay_" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:20]
    return {"schema_version": REPLAY_SCHEMA_VERSION, "replay_id": replay_id, "created_at": utc_now(), **payload}


def save_replay(replay):
    if not isinstance(replay, dict) or replay.get("schema_version") != REPLAY_SCHEMA_VERSION:
        raise ValueError("replay has an unsupported schema version.")
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = [row for row in list_replays() if row.get("replay_id") != replay.get("replay_id")]
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in [*existing, replay]:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    return {"saved": True, "replay_id": replay["replay_id"], "path": str(path)}


def list_replays():
    path = _path()
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def replay_action(action, request):
    if action == "compare":
        return compare_cases(request.get("task", ""), request.get("cases"))
    if action == "save":
        replay = request.get("replay") or compare_cases(request.get("task", ""), request.get("cases"))
        return save_replay(replay)
    if action == "list":
        return {"replays": list_replays()}
    if action == "get":
        replay_id = request.get("replay_id")
        return next((row for row in list_replays() if row.get("replay_id") == replay_id), None) or {"replay_id": replay_id, "found": False}
    raise ValueError("replay action must be compare, save, list, or get.")
