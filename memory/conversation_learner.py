from memory.capture import capture_memory
from memory.mistake_capture import capture_mistake
from memory.parse_everything import parse_everything
from memory.principle_capture import capture_principles
from memory.quality import (
    is_valid_experience,
    is_valid_principle,
    is_valid_reflection
)
from memory.reflection_capture import capture_reflection


def learn_from_conversation(
        conversation,
        agent_id="human"):
    from memory.extract_everything import extract_everything

    text = extract_everything(conversation)
    learned = parse_everything(text)

    # Return only records that passed admission and were persisted.
    accepted = {
        "reflections": [],
        "principles": [],
        "mistakes": []
    }

    experience = learned.get("experience")

    if is_valid_experience(experience):
        capture_memory(
            task=experience["task"],
            files=experience["files"],
            summary=experience["summary"],
            solution=experience["solution"],
            importance=5,
            memory_type="experience",
            owner=agent_id
        )

        accepted["experience"] = experience

    for reflection in learned.get("reflections", []):
        if not is_valid_reflection(reflection):
            continue

        capture_reflection(
            reflection,
            owner=agent_id
        )

        accepted["reflections"].append(reflection)

    principles = [
        principle
        for principle in learned.get("principles", [])
        if is_valid_principle(principle)
    ]

    if principles:
        capture_principles(
            principles,
            owner=agent_id
        )

        accepted["principles"] = principles

    for mistake in learned.get("mistakes", []):
        if not is_valid_experience(mistake):
            continue

        capture_mistake(
            task=mistake["task"],
            files=mistake["files"],
            summary=mistake["summary"],
            solution=mistake["solution"],
            owner=agent_id
        )

        accepted["mistakes"].append(mistake)

    return accepted
