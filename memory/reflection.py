from collections import Counter


def reflect(memories):

    file_counter = Counter()

    task_counter = Counter()

    for memory in memories:

        task_counter[memory["task"]] += 1

        for file in memory["files"]:
            file_counter[file] += 1

    return {
        "files": file_counter,
        "tasks": task_counter
    }