from memory.capture import capture_memory

from memory.reflection_capture import (
    capture_reflection
)

from memory.principle_capture import (
    capture_principles
)

from memory.mistake_capture import (
    capture_mistake
)

from memory.extract_everything import (
    extract_everything
)

from memory.parse_everything import (
    parse_everything
)

from memory.auto_learn import (
    learn_from_solution
)


def valid_text(x):

    if x is None:
        return False

    x = str(x).strip().lower()

    bad = {

        "",
        "...",
        "unknown",
        "describe the problem",
        "identify a coding experience from the conversation",
        "none",
        "n/a",
        "na"

    }

    return x not in bad


def learn_from_conversation(
        conversation,
        agent_id="human"):

    text = extract_everything(
        conversation
    )

    learned = parse_everything(
        text
    )

    # -----------------------
    # EXPERIENCE
    # -----------------------

    if "experience" in learned:

        experience = learned["experience"]

        if (

            valid_text(
                experience.get(
                    "task",
                    ""
                )
            )

            and

            valid_text(
                experience.get(
                    "summary",
                    ""
                )
            )

        ):

            capture_memory(

                task=experience["task"],

                files=experience["files"],

                summary=experience["summary"],

                solution=experience["solution"],

                importance=5,

                memory_type="experience",

                owner=agent_id

            )

    # -----------------------
    # REFLECTIONS
    # -----------------------

    if "reflections" in learned:

        for reflection in learned["reflections"]:

            if not valid_text(
                    reflection):
                continue

            capture_reflection(

                reflection,

                owner=agent_id

            )

    # -----------------------
    # PRINCIPLES
    # -----------------------

    if "principles" in learned:

        good_principles = []

        for principle in learned["principles"]:

            if not valid_text(
                    principle):
                continue

            good_principles.append(
                principle
            )

        capture_principles(

            good_principles,

            owner=agent_id

        )

    # -----------------------
    # MISTAKES
    # -----------------------

    if "mistakes" in learned:

        for mistake in learned["mistakes"]:

            if (

                not valid_text(

                    mistake.get(
                        "task",
                        ""
                    )

                )

                or

                not valid_text(

                    mistake.get(
                        "summary",
                        ""
                    )

                )

            ):

                continue

            capture_mistake(

                task=mistake["task"],

                files=mistake["files"],

                summary=mistake["summary"],

                solution=mistake["solution"],

                owner=agent_id

            )

    return learned