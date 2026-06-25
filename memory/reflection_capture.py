from memory.extractor import extract_memory
from memory.store import add_memory


def capture_reflection(
        reflection,
        owner="shared"):

    memory = extract_memory(

        task=reflection,

        files=["reflection"],

        summary=reflection,

        solution="Observation",

        importance=8,

        memory_type="reflection"

    )

    memory["owner"] = owner

    add_memory(
        memory
    )

    return memory