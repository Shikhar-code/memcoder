def score_memory(memory, query=""):

    score = 0

    task = memory["task"].lower()
    summary = memory["summary"].lower()

    # importance × confidence
    importance = memory.get(
        "importance",
        5
    )

    confidence = memory.get(
        "confidence",
        1.0
    )

    frequency = memory.get(
        "frequency",
        1
    )

    score += importance * confidence

    # repeated memories become easier to retrieve
    score += 0.5 * frequency

    # keyword overlap
    query_words = query.lower().split()

    for word in query_words:

        if word in task:
            score += 3

        if word in summary:
            score += 1

    # multi-file memories slightly favored
    score += len(
        memory.get(
            "files",
            []
        )
    )

    # better embedding distance = higher score
    score -= memory["score"]

    return score