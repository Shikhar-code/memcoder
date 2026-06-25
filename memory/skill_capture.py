from memory.capture import capture_memory


def capture_skill(skill):

    return capture_memory(
        task=skill,
        files=["skill"],
        summary=skill,
        solution="Principle",
        importance=10
    )