import json

from memory.extractor import extract_memory
from memory.store import add_memory


def capture_reflection(
        reflection,
        owner="shared",
        source_experience_id=None,
        verification=None):

    memory = extract_memory(

        task=reflection,

        files=["reflection"],

        summary=reflection,

        solution="Observation",

        importance=8,

        memory_type="reflection"

    )

    memory["owner"] = owner

    if source_experience_id:
        memory["source_experience_id"] = source_experience_id
    if verification:
        memory["verification"] = json.dumps(verification, sort_keys=True)

    add_memory(
        memory
    )

    return memory
