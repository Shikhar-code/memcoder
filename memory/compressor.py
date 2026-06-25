def compress_memories(memories):

    output = ""

    output += (
        "HIGH-LEVEL OBSERVATIONS\n"
        "=======================\n\n"
    )

    composition_related = 0
    duration_related = 0

    files_seen = set()

    for memory in memories:

        for file in memory["files"]:
            files_seen.add(file)

        task = memory["task"].lower()

        if "duration" in task:
            duration_related += 1

        if "composition" in task:
            composition_related += 1

    if duration_related > 0:
        output += (
            "• Duration-related issues have occurred previously.\n"
        )

    if composition_related > 0:
        output += (
            "• Composition registration problems have been seen before.\n"
        )

    if len(files_seen) > 0:
        output += (
            f"• Frequently involved files: {', '.join(files_seen)}\n"
        )

    return output