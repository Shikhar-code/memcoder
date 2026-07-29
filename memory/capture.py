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
        source=None,
        verification=None,
        metadata=None,
        environment=None):

    task = normalize_task(task)

    files = normalize_files(files)

    memory = extract_memory(

        task,

        files,

        summary,

        solution,

        importance,

        memory_type,
        source,
        verification

    )

    memory["owner"] = owner

    if environment is not None:
        from memory.validity import attach_environment
        attach_environment(memory, environment)

    for key, value in (metadata or {}).items():
        if key not in memory:
            memory[key] = value

    add_memory(
        memory
    )

    return memory
