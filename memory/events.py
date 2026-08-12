"""Small idempotent event journal for host and Studio integrations."""

import hashlib
import json
import os
from pathlib import Path

from memory.records import utc_now


def journal_path():
    configured = os.environ.get("MEMCODER_EVENT_JOURNAL_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_events.jsonl"


def _read(path=None):
    path = Path(path or journal_path())
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


def append_event(event):
    if not isinstance(event, dict):
        raise ValueError("event must be an object.")
    event = dict(event)
    event_id = str(event.get("event_id") or "").strip()
    if not event_id:
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        event_id = "evt_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
    existing = next((row for row in _read() if row.get("event_id") == event_id), None)
    if existing:
        return {**existing, "deduplicated": True}
    stored = {**event, "event_id": event_id, "timestamp": event.get("timestamp") or utc_now()}
    path = journal_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(stored, sort_keys=True, ensure_ascii=False) + "\n")
    return stored


def list_events(*, owner=None, task_id=None, limit=100):
    rows = _read()
    if owner is not None:
        rows = [row for row in rows if row.get("owner") == owner]
    if task_id is not None:
        rows = [row for row in rows if row.get("task_id") == task_id]
    return rows[-max(1, int(limit)):]


def journal_status():
    path = journal_path()
    return {"path": str(path), "exists": path.exists(), "events": len(_read(path))}
