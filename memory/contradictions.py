"""Evidence-preserving contradiction reporting and explicit resolution."""

from memory.provenance import link
from memory.record_store import get_record
from memory.validity import set_record_validity


def _owned_pair(first_id, second_id, owner):
    if first_id == second_id:
        raise ValueError("A contradiction requires two different record IDs.")
    first = get_record(first_id)
    second = get_record(second_id)
    if first is None or second is None:
        raise ValueError("Both contradiction records must exist.")
    if first.get("owner") != owner or second.get("owner") != owner:
        raise ValueError("Contradiction records must belong to the requesting owner.")
    return first, second


def report_contradiction(first_id, second_id, owner, reason):
    """Preserve conflicting evidence and withhold both records from auto reuse."""
    if not isinstance(reason, str) or len(reason.strip().split()) < 3:
        raise ValueError("contradiction reason must be a meaningful sentence.")
    first, second = _owned_pair(first_id, second_id, owner)
    metadata = {"reason": reason.strip()}
    link(first["record_id"], second["record_id"], "contradicts", owner, metadata)
    link(second["record_id"], first["record_id"], "contradicts", owner, metadata)
    set_record_validity(first["record_id"], "contradicted", owner=owner, reason=reason)
    set_record_validity(second["record_id"], "contradicted", owner=owner, reason=reason)
    return {
        "reported": [first["record_id"], second["record_id"]],
        "automatic_retrieval_withheld": True,
        "reason": reason.strip(),
    }


def resolve_contradiction(winner_id, loser_id, owner, reason):
    """Restore a reviewed winner and retain the losing evidence as superseded."""
    if not isinstance(reason, str) or len(reason.strip().split()) < 3:
        raise ValueError("resolution reason must be a meaningful sentence.")
    winner, loser = _owned_pair(winner_id, loser_id, owner)
    set_record_validity(winner["record_id"], "trusted", owner=owner, reason=reason)
    set_record_validity(loser["record_id"], "superseded", owner=owner, reason=reason)
    link(winner["record_id"], loser["record_id"], "supersedes", owner, {"reason": reason.strip()})
    return {
        "winner_id": winner["record_id"],
        "loser_id": loser["record_id"],
        "winner_state": "trusted",
        "loser_state": "superseded",
    }
