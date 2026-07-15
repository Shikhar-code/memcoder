from memory.chroma_client import collection
from memory.normalize import normalize_task


def find_similar_memories(
        task,
        memory_type=None,
        owner=None):

    task = normalize_task(task)

    data = collection.get()

    memories = []

    for metadata in data["metadatas"]:

        memory_task = normalize_task(
            metadata.get(
                "task",
                ""
            )
        )

        if memory_task != task:
            continue

        if memory_type is not None:

            if metadata.get(
                    "type"
            ) != memory_type:

                continue

        if owner is not None:

            if metadata.get(
                    "owner"
            ) != owner:

                continue

        memories.append(
            metadata
        )

    return memories


def merge_memories(memories):

    if len(memories) == 0:
        return None

    merged = {}

    # shortest task
    merged["task"] = min(
        [m["task"] for m in memories],
        key=len
    )

    # files
    files = []

    bad_files = {
        "unknown",
        "...",
        "ollama.chat()",
        "response.py"
    }

    for m in memories:

        files.extend(
            m.get(
                "files",
                []
            )
        )

    merged["files"] = [

        f

        for f in list(
            dict.fromkeys(files)
        )

        if f not in bad_files

    ]

    if len(merged["files"]) == 0:

        merged["files"] = ["unknown"]

    # longest summary
    merged["summary"] = max(

        [m["summary"] for m in memories],

        key=len

    )

    # longest solution
    merged["solution"] = max(

        [m["solution"] for m in memories],

        key=len

    )

    merged["importance"] = (

        max(
            m["importance"]
            for m in memories
        )

        +

        len(memories) // 2

    )

    merged["confidence"] = min(

        1.0,

        max(
            m.get(
                "confidence",
                1.0
            )

            for m in memories
        )

        +

        0.05 * (
            len(memories) - 1
        )

    )

    merged["type"] = memories[0]["type"]

    merged["owner"] = memories[0].get(
        "owner",
        "shared"
    )

    merged["frequency"] = len(memories)

    return merged
