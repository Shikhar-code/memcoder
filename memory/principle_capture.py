from memory.extractor import extract_memory
from memory.store import add_memory
from memory.provenance import link
from memory.records import record_id


def capture_principles(
        principles,
        owner="shared",
        source=None,
        source_experience_id=None,
        environment=None):

    memories = []

    for principle in principles:

        memory = extract_memory(

            task=principle,

            files=["principle"],

            summary=principle,

            solution="Principle",

            importance=10,

            memory_type="principle",
            source=source

        )

        memory["owner"] = owner
        if environment is not None:
            from memory.validity import attach_environment
            attach_environment(memory, environment)

        stored = add_memory(memory)
        if source_experience_id:
            link(
                record_id(stored),
                source_experience_id,
                "derived_from",
                owner,
            )

        memories.append(
            stored
        )

    return memories
