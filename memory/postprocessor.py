def postprocess_memory(memory):

    task = memory["task"].lower().strip()

    generic_phrases = [
        "memory extraction",
        "extract software memory",
        "extract software memory from the conversation",
        "extract a software memory from the conversation"
    ]

    if task in generic_phrases:
        memory["task"] = memory["summary"]

    # shorten overly verbose tasks

    if "durationinframes" in memory["summary"].lower():
        memory["task"] = "durationInFrames became zero"

    return memory