import json

from memory.extractor import extract_memory
from memory.store import add_memory
from memory.provenance import link
from memory.records import record_id


def capture_reflection(
        reflection,
        owner="shared",
        source_experience_id=None,
        verification=None,
        environment=None):

    memory = extract_memory(

        task=reflection,

        files=["reflection"],

        summary=reflection,

        solution="Observation",

        importance=8,

        memory_type="reflection"

    )

    memory["owner"] = owner

    if environment is not None:
        from memory.validity import attach_environment
        attach_environment(memory, environment)

    if source_experience_id:
        memory["source_experience_id"] = source_experience_id
    if verification:
        memory["verification"] = json.dumps(verification, sort_keys=True)

    stored = add_memory(memory)
    if source_experience_id:
        link(
            record_id(stored),
            source_experience_id,
            "derived_from",
            owner,
        )

    return stored
