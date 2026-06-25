import re


def normalize_task(task):

    task = task.strip()

    prefixes = [

        r"^Fix the issue where\s+",
        r"^Fix\s+",
        r"^Investigate why\s+",
        r"^Check why\s+",
        r"^Debug\s+",
        r"^Resolve\s+",
        r"^Troubleshoot\s+"

    ]

    for prefix in prefixes:

        task = re.sub(
            prefix,
            "",
            task,
            flags=re.IGNORECASE
        )

    task = task.strip()

    if task.endswith("."):

        task = task[:-1]

    task = task.strip()

    task = task.rstrip(".")

    task = task.lower()

    return task.strip().rstrip(".").lower()
def normalize_files(files):

    normalized = []

    bad_files = {

        "response.py",
        "ollama.chat()",
        "thinking",
        "content",
        "unknown"
    }

    for file in files:

        file = file.strip()

        if file.lower() in bad_files:

            continue

        normalized.append(file)

    if len(normalized) == 0:

        normalized = ["unknown"]

    return list(dict.fromkeys(normalized))