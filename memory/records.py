"""Stable identity and lifecycle metadata for guidance records.

Chroma remains the retrieval index for now.  These helpers make the metadata
safe to evolve by separating a record's stable identity from its mutable
content fingerprint.
"""

from datetime import datetime, timezone
from uuid import uuid4

from memory.memory_hash import memory_hash


GUIDANCE_RECORD_SCHEMA_VERSION = 2
VALID_RECORD_STATES = {
    "candidate",
    "trusted",
    "superseded",
    "contradicted",
    "deprecated",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def record_id(memory):
    """Return the stable ID, falling back to Beta 2.0's legacy hash ID."""
    return memory.get("record_id") or memory.get("hash", "")


def initialize_record(memory):
    """Add stable metadata to a new record without changing its content."""
    now = utc_now()
    memory.setdefault("record_id", f"mem_{uuid4().hex}")
    memory.setdefault("schema_version", GUIDANCE_RECORD_SCHEMA_VERSION)
    memory.setdefault("record_state", "trusted")
    if memory["record_state"] not in VALID_RECORD_STATES:
        raise ValueError("record_state must be a supported lifecycle state.")
    memory.setdefault("created_at", now)
    memory.setdefault("updated_at", now)
    memory.setdefault("revision", 1)
    memory["content_hash"] = memory_hash(memory)
    # `hash` remains a compatibility alias for callers that have not migrated.
    memory["hash"] = memory["content_hash"]
    return memory


def revise_record(memory):
    """Apply a mutation while preserving identity and recording a revision."""
    memory.setdefault("record_id", memory.get("hash", f"mem_{uuid4().hex}"))
    memory.setdefault("created_at", utc_now())
    memory["schema_version"] = GUIDANCE_RECORD_SCHEMA_VERSION
    memory["revision"] = int(memory.get("revision", 1)) + 1
    memory["updated_at"] = utc_now()
    memory.setdefault("record_state", "trusted")
    if memory["record_state"] not in VALID_RECORD_STATES:
        raise ValueError("record_state must be a supported lifecycle state.")
    memory["content_hash"] = memory_hash(memory)
    memory["hash"] = memory["content_hash"]
    return memory


def searchable_document(memory):
    """Build the only text that belongs in the semantic guidance index."""
    return f"""
Task:
{memory['task']}

Files:
{', '.join(memory['files'])}

Summary:
{memory['summary']}

Solution:
{memory['solution']}
"""
