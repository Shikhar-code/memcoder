def postprocess_meta_skill(raw_meta_skill):

    text = raw_meta_skill.lower()

    meta_skills = []

    if (
        "robustness" in text
        or "prevent failures" in text
    ):
        meta_skills.append(
            "Prefer robustness over assumptions."
        )

    if (
        "consistency" in text
        or "structure" in text
    ):
        meta_skills.append(
            "Value consistency."
        )

    if (
        "prevent failures" in text
        or "anticipate" in text
    ):
        meta_skills.append(
            "Prevent failures before they occur."
        )

    return meta_skills