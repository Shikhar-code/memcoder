from memory.relevance import filter_trusted_memories


def build_hierarchical_context(
        results,
        query=""):

    sections = []

    experiences = filter_trusted_memories(
        results.get("experiences", []),
        query=query
    )
    mistakes = filter_trusted_memories(
        results.get("mistakes", []),
        query=query
    )
    principles = filter_trusted_memories(
        results.get("principles", []),
        query=query
    )
    reflections = filter_trusted_memories(
        results.get("reflections", []),
        query=query
    )

    if experiences:
        sections.append("PAST EXPERIENCES\n")

        for memory in experiences:

            files = memory.get("files", [])

            if isinstance(files, list):
                files_text = ", ".join(files)
            else:
                files_text = str(files)

            sections.append(
                f"""Problem:
{memory.get("task", "Unknown")}

Context:
{memory.get("summary", "No summary available.")}

Files:
{files_text}

Fix:
{memory.get("solution", "No solution available.")}
──────
"""
            )

    if mistakes:
        sections.append("\nAVOID\n")

        for memory in mistakes:

            files = memory.get("files", [])

            if isinstance(files, list):
                files_text = ", ".join(files)
            else:
                files_text = str(files)

            sections.append(
                f"""{memory.get("summary", memory.get("task", "Unknown"))}

Files:
{files_text}

Fix:
{memory.get("solution", "No solution available.")}
──────
"""
            )

    if principles:
        sections.append("\nRULES\n")

        for memory in principles:
            sections.append(
                f"""{memory.get("summary", memory.get("task", "Unknown"))}
──────
"""
            )

    if reflections:
        sections.append(
            "\nOBSERVATIONS\n"
            "Use these observations to choose what to verify first. "
            "They are process guidance, not proof of a root cause.\n"
        )

        for memory in reflections:
            sections.append(
                f"""{memory.get("summary", memory.get("task", "Unknown"))}
──────
"""
            )

    return "\n".join(sections)
