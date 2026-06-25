import ollama


def create_meta_skill_llm(skills):

    skill_text = "\n".join(skills)

    prompt = f"""
You are analyzing software engineering skills.

Convert them into higher-level philosophies.

Examples:

Skills:

- Always validate inputs.
- Use defensive programming.
- Maintain consistent structures.

Meta-skills:

- Prefer robustness over assumptions.
- Value consistency.
- Prevent failures before they occur.

-------------------------

Skills:

{skill_text}

Meta-skills:
"""

    response = ollama.chat(
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