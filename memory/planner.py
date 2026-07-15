from llm.optional_ollama import get_ollama


def create_plan(problem,
                experiences,
                reflections,
                skills,
                meta_skills):

    experience_text = "\n".join(
        [m["task"] for m in experiences]
    )

    reflection_text = "\n".join(
        [m["task"] for m in reflections]
    )

    skill_text = "\n".join(skills)

    meta_skill_text = "\n".join(meta_skills)

    prompt = f"""
Current problem:

{problem}

Relevant experiences:

{experience_text}

Relevant observations:

{reflection_text}

Skills:

{skill_text}

Meta-skills:

{meta_skill_text}

Create a debugging plan.

Return 5-10 numbered steps.
"""

    response = get_ollama().chat(
        model="qwen2.5-coder:3b",
        think=False,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]
