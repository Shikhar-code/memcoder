import re


def parse_numbered_section(section_text):

    pattern = r"\d+\.\s*(.*)"

    matches = re.findall(
        pattern,
        section_text
    )

    return [

        x.strip()

        for x in matches

        if x.strip()

    ]


def parse_everything(text):

    # EXPERIENCE

    task = re.search(
        r"EXPERIENCE.*?TASK:\s*(.*?)\n\s*FILES:",
        text,
        re.DOTALL
    )

    files = re.search(
        r"EXPERIENCE.*?FILES:\s*(.*?)\n\s*SUMMARY:",
        text,
        re.DOTALL
    )

    summary = re.search(
        r"EXPERIENCE.*?SUMMARY:\s*(.*?)\n\s*SOLUTION:",
        text,
        re.DOTALL
    )

    solution = re.search(
        r"EXPERIENCE.*?SOLUTION:\s*(.*?)-{5,}",
        text,
        re.DOTALL
    )

    experience = {

        "task":
            task.group(1).strip(),

        "files":
            [
                x.strip()
                for x in files.group(1).split(",")
            ],

        "summary":
            summary.group(1).strip(),

        "solution":
            solution.group(1).strip()

    }

    # REFLECTIONS

    reflection_block = re.search(

        r"REFLECTIONS(.*?)PRINCIPLES",

        text,

        re.DOTALL

    )

    reflections = []

    if reflection_block:

        reflections = parse_numbered_section(

            reflection_block.group(1)

        )

    # PRINCIPLES

    principle_block = re.search(

        r"PRINCIPLES(.*?)MISTAKES",

        text,

        re.DOTALL

    )

    principles = []

    if principle_block:

        principles = parse_numbered_section(

            principle_block.group(1)

        )

    # MISTAKES

    mistake_block = re.search(

        r"MISTAKES(.*)",

        text,

        re.DOTALL

    )

    mistakes = []

    if mistake_block:

        pattern = r"""
TASK:\s*(.*?)\n
FILES:\s*(.*?)\n
SUMMARY:\s*(.*?)\n
SOLUTION:\s*(.*?)
(?=\n\s*TASK:|\Z)
"""

        matches = re.findall(

            pattern,

            mistake_block.group(1),

            re.DOTALL | re.VERBOSE

        )

        for task, files, summary, solution in matches:

            mistakes.append({

                "task":
                    task.strip(),

                "files":
                    [
                        x.strip()
                        for x in files.split(",")
                    ],

                "summary":
                    summary.strip(),

                "solution":
                    solution.strip()

            })

    return {

        "experience": experience,

        "reflections": reflections,

        "principles": principles,

        "mistakes": mistakes

    }