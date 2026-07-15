import re


def parse_numbered_section(section_text):
    matches = re.findall(
        r"\d+\.\s*(.*)",
        section_text
    )

    return [
        match.strip()
        for match in matches
        if match.strip()
    ]


def parse_labeled_memory(block):
    fields = {}

    for field in [
            "TASK",
            "FILES",
            "SUMMARY",
            "SOLUTION"]:

        match = re.search(
            rf"^\s*{field}:\s*(.*?)(?=^\s*(?:TASK|FILES|SUMMARY|SOLUTION):|\Z)",
            block,
            re.DOTALL | re.MULTILINE | re.IGNORECASE
        )

        if not match:
            return None

        fields[field.lower()] = match.group(1).strip()

    return {
        "task": fields["task"],
        "files": [
            file.strip()
            for file in fields["files"].split(",")
            if file.strip()
        ],
        "summary": fields["summary"],
        "solution": fields["solution"]
    }


def parse_everything(text):
    experience_block = re.search(
        r"EXPERIENCE\s*(.*?)(?:-{5,}|REFLECTIONS\b|\Z)",
        text,
        re.DOTALL | re.IGNORECASE
    )

    experience = None

    if experience_block:
        experience = parse_labeled_memory(
            experience_block.group(1)
        )

    reflection_block = re.search(
        r"REFLECTIONS(.*?)PRINCIPLES",
        text,
        re.DOTALL | re.IGNORECASE
    )

    reflections = []

    if reflection_block:
        reflections = parse_numbered_section(
            reflection_block.group(1)
        )

    principle_block = re.search(
        r"PRINCIPLES(.*?)MISTAKES",
        text,
        re.DOTALL | re.IGNORECASE
    )

    principles = []

    if principle_block:
        principles = parse_numbered_section(
            principle_block.group(1)
        )

    mistake_block = re.search(
        r"MISTAKES(.*)",
        text,
        re.DOTALL | re.IGNORECASE
    )

    mistakes = []

    if mistake_block:
        blocks = re.split(
            r"(?=^\s*TASK:)",
            mistake_block.group(1),
            flags=re.MULTILINE | re.IGNORECASE
        )

        for block in blocks:
            memory = parse_labeled_memory(block)

            if memory:
                mistakes.append(memory)

    return {
        "experience": experience,
        "reflections": reflections,
        "principles": principles,
        "mistakes": mistakes
    }
