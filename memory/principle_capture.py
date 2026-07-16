from memory.extractor import extract_memory
from memory.store import add_memory


def capture_principles(
        principles,
        owner="shared",
        source=None):

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

        add_memory(
            memory
        )

        memories.append(
            memory
        )

    return memories
