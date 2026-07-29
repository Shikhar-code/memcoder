"""Evidence-graph semantics built on the durable local record store."""

import json

from memory.record_store import add_edge, edges_for, list_records
from memory.records import record_id


VALID_EDGE_RELATIONS = {
    "derived_from",
    "supports",
    "validated_by",
    "supersedes",
    "contradicts",
}


def link(source_id, target_id, relation, owner, metadata=None):
    """Create one explicit evidence/provenance relationship."""
    add_edge(source_id, target_id, relation, owner, metadata=metadata)
    return {
        "source_id": source_id,
        "target_id": target_id,
        "relation": relation,
        "owner": owner,
    }


def trace(memory_id, owner=None):
    """Return direct, inspectable evidence surrounding a memory."""
    return edges_for(memory_id, owner=owner)


def _json_list(value):
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
    except (TypeError, json.JSONDecodeError):
        return []
    return parsed if isinstance(parsed, list) else []


def backfill_existing_provenance():
    """Recover graph links already represented by legacy record metadata."""
    created = 0
    for memory in list_records():
        memory_id = record_id(memory)
        owner = memory.get("owner", "shared")
        targets = []
        if memory.get("type") == "reflection" and memory.get("source_experience_id"):
            targets.append((memory_id, memory["source_experience_id"], "derived_from"))
        if memory.get("type") == "skill":
            for support_id in _json_list(memory.get("supporting_experience_ids")):
                targets.append((support_id, memory_id, "supports"))
            for support_id in _json_list(memory.get("supporting_principle_ids")):
                targets.append((support_id, memory_id, "supports"))
        for source_id, target_id, relation in targets:
            try:
                created += add_edge(source_id, target_id, relation, owner)
            except ValueError:
                # Incomplete legacy references are preserved in the record but
                # never fabricated into graph links.
                continue
    return {"processed": len(list_records()), "links_considered": created}
