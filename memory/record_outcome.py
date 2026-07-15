"""Provider-free recording of a solved agent outcome."""

from memory.capture import capture_memory
from memory.principle_capture import capture_principles
from memory.quality import (
    is_valid_experience,
    is_valid_principle,
    is_valid_reflection
)
from memory.reflection_capture import capture_reflection


def record_outcome(
        task,
        files,
        summary,
        solution,
        reflection=None,
        principles=None,
        agent_id="human"):
    """Persist only structured memories supplied by the calling agent."""

    experience = {
        "task": task,
        "files": files,
        "summary": summary,
        "solution": solution
    }

    recorded = {
        "experience": None,
        "reflections": [],
        "principles": [],
        "rejected": []
    }

    if is_valid_experience(experience):
        capture_memory(
            task=task,
            files=files,
            summary=summary,
            solution=solution,
            importance=5,
            memory_type="experience",
            owner=agent_id
        )

        recorded["experience"] = experience
    else:
        recorded["rejected"].append(
            "experience: task, files, summary, and solution must be meaningful"
        )

    if reflection and is_valid_reflection(reflection):
        capture_reflection(
            reflection,
            owner=agent_id
        )

        recorded["reflections"].append(reflection)
    elif reflection:
        recorded["rejected"].append(
            "reflection: use one short 'I ...' investigation observation; "
            "do not describe a fix or state a principle"
        )

    valid_principles = [
        principle
        for principle in (principles or [])
        if is_valid_principle(principle)
    ]

    if valid_principles:
        capture_principles(
            valid_principles,
            owner=agent_id
        )

        recorded["principles"] = valid_principles

    invalid_principles = len(principles or []) - len(valid_principles)
    if invalid_principles:
        recorded["rejected"].append(
            f"principles: {invalid_principles} item(s) were not meaningful"
        )

    return recorded
