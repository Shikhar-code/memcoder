def score_importance(memory):

    score = 5

    task = memory.get("task", "").lower()

    if "gpu" in task:
        score += 2

    if "crash" in task:
        score += 2

    if "error" in task:
        score += 1

    if "failed" in task:
        score += 1

    if "corrupt" in task:
        score += 2

    if "memory leak" in task:
        score += 2

    files = memory.get("files", [])

    if len(files) > 1:
        score += 1

    return min(score, 10)