import ollama


def create_skill_llm(reflection):

    prompt = f"""
You are analyzing software reflections.

Convert the reflection into 1-3 reusable principles.

Examples:

Reflection:
Validation problems repeatedly occur.

Skills:

- Always validate inputs.
- Use defensive programming.

--------------------------------

Reflection:

{reflection}

Skills:
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