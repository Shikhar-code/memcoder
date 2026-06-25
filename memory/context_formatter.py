def format_context(memories, task):

    output = ""

    output += (
        "CURRENT TASK\n"
        "============\n"
    )

    output += f"{task}\n\n"

    experiences = [
        m for m in memories
        if m["type"] == "experience"
    ]

    reflections = [
        m for m in memories
        if m["type"] == "reflection"
    ]

    principles = [
        m for m in memories
        if m["type"] == "principle"
    ]

    mistakes = [
        m for m in memories
        if m["type"] == "mistake"
    ]

    # Experiences
    output += (
        "RELATED EXPERIENCES\n"
        "===================\n\n"
    )

    for i, memory in enumerate(experiences, start=1):

        output += (
            f"{i}. {memory['task']}\n\n"

            f"Summary:\n"
            f"{memory['summary']}\n\n"

            f"Files:\n"
            f"{', '.join(memory['files'])}\n\n"

            f"Fix:\n"
            f"{memory['solution']}\n\n"

            "-------------------------\n\n"
        )

    # Reflections
    output += (
        "OBSERVATIONS\n"
        "============\n\n"
    )

    for i, memory in enumerate(reflections, start=1):

        output += (
            f"{i}. {memory['summary']}\n\n"

            "-------------------------\n\n"
        )

    # Principles
    output += (
        "PRINCIPLES\n"
        "==========\n\n"
    )

    for memory in principles:

        output += (
            f"• {memory['task']}\n"
        )

    output += "\n\n"

    # Mistakes
    output += (
        "COMMON MISTAKES\n"
        "===============\n\n"
    )

    for memory in mistakes:

        output += (
            f"• {memory['task']}\n"
        )

    output += "\n"

    return output