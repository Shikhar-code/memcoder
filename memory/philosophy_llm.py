import ollama


def philosophy_llm(principles):

    text = ""

    for i, principle in enumerate(principles, 1):

        text += f"""
Principle {i}

{principle}

-------------------
"""

    prompt = f"""
You are analyzing engineering principles.

Compress them into deeper philosophies.

A philosophy is broader and more timeless than a principle.

Examples:

Principles:
- Test continuously.
- Make failures observable.

Possible philosophy:
- Prevent failures before they occur.

Principles:
- Follow interfaces strictly.
- Maintain clear documentation.

Possible philosophy:
- Prefer explicitness over assumptions.

Return ONLY bullet points.

No explanations.
No introductions.
No conversational language.

Principles:

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