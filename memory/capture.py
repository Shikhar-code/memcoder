from memory.extractor import extract_memory
from memory.store import add_memory
from memory.normalize import (
    normalize_task,
    normalize_files
)


def capture_memory(
        task,
        files,
        summary,
        solution,
        importance=5,
        memory_type="experience",
        owner="shared",
        source=None):

    task = normalize_task(task)

    files = normalize_files(files)

    memory = extract_memory(

        task,

        files,

        summary,

        solution,

        importance,

        memory_type,
        source

    )

    memory["owner"] = owner

    add_memory(
        memory
    )

    return memory
