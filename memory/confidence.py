def confidence_score(memory):

    confidence = 1.0

    if memory["type"] == "reflection":
        confidence *= 0.8

    if memory["type"] == "principle":
        confidence *= 0.8

    if memory["type"] == "mistake":
        confidence *= 0.7

    if memory["files"] == ["unknown"]:
        confidence *= 0.7

    return round(confidence,2)