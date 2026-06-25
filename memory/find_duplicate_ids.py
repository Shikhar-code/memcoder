from memory.chroma_client import collection
from memory.normalize import normalize_task


def find_duplicate_ids(
        task,
        memory_type=None):

    task = normalize_task(task)

    data = collection.get()

    ids = data["ids"]
    metadatas = data["metadatas"]

    duplicate_ids = []

    for memory_id, metadata in zip(
            ids,
            metadatas):

        task = normalize_task(task)

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
                    "type") != memory_type:

                continue

        duplicate_ids.append(
            memory_id
        )

    return duplicate_ids