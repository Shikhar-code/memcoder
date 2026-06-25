import ollama


def reflect_corpus(reflections):

    text = ""

    for i, reflection in enumerate(reflections, 1):

        text += f"""
Reflection {i}

{reflection}

-------------------
"""

    prompt = f"""
You are analyzing local reflections from many software domains.

Find patterns that recur across domains.

Focus on:

1. Common causes of failures.
2. Common solution strategies.
3. General debugging principles.
4. Practices that prevent bugs.

Return ONLY bullet points.

No introduction.
No explanations.
No conversational language.

Reflections:

{text}
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