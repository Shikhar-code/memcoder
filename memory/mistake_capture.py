from memory.extractor import extract_memory
from memory.store import add_memory


def capture_mistake(
        task,
        files,
        summary,
        solution,
        owner="shared"):

    memory = extract_memory(

        task=task,

        files=files,

        summary=summary,

        solution=solution,

        importance=9,

        memory_type="mistake"

    )

    memory["owner"] = owner

    add_memory(
        memory
    )

    return memory