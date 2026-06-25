from memory.capture import capture_memory


def capture_meta_skill(meta_skill):

    return capture_memory(
        task=meta_skill,
        files=["meta_skill"],
        summary=meta_skill,
        solution="Philosophy",
        importance=10
    )