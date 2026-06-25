def postprocess_skill(raw_skill):

    text = raw_skill.lower()

    skills = []

    if (
        "defensive programming" in text
    ):
        skills.append(
            "Use defensive programming."
        )

    if (
        "validation" in text
        or "runtime" in text
    ):
        skills.append(
            "Always validate inputs."
        )

    if (
        "consistency" in text
        or "memory structure" in text
    ):
        skills.append(
            "Maintain consistent structures."
        )

    if (
        "error message patterns" in text
        or "recurring patterns" in text
    ):
        skills.append(
            "Look for recurring error patterns."
        )

    return skills