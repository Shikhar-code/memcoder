from memory.capture import capture_memory
from memory.reflection_capture import capture_reflection
from memory.principle_capture import capture_principles
from memory.mistake_capture import capture_mistake


def learn_from_solution(
        task,
        files,
        summary,
        solution,
        principles=None,
        observations=None,
        mistakes=None
):

    if principles is None:
        principles = []

    if observations is None:
        observations = []

    if mistakes is None:
        mistakes = []

    # Experience
    capture_memory(
        task=task,
        files=files,
        summary=summary,
        solution=solution
    )

    # Reflections
    for observation in observations:

        capture_reflection(
            observation
    )

    # Principles
    capture_principles(
        principles
    )

    # Mistakes
    for mistake in mistakes:

        capture_mistake(
            task=mistake["task"],
            files=mistake["files"],
            summary=mistake["summary"],
            solution=mistake["solution"]
        )