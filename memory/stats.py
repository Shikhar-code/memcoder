from memory.chroma_client import collection


def memory_stats():

    data = collection.get()

    experiences = 0
    mistakes = 0
    principles = 0
    reflections = 0

    for metadata in data["metadatas"]:

        memory_type = metadata.get(
            "type",
            ""
        )

        if memory_type == "experience":

            experiences += 1

        elif memory_type == "mistake":

            mistakes += 1

        elif memory_type == "principle":

            principles += 1

        elif memory_type == "reflection":

            reflections += 1

    return {

        "experiences": experiences,

        "mistakes": mistakes,

        "principles": principles,

        "reflections": reflections,

        "total": len(data["ids"])

    }