import ollama


def reflect_llm(memories):

    text = ""

    for i, memory in enumerate(memories, 1):

        files = memory.get("files", [])

        # Handle malformed files field
        if files is None:
            files = []

        if isinstance(files, str):
            files = [files]

        if not isinstance(files, list):
            files = []

        text += f"""
Memory {i}

Task:
{memory.get('task', '')}

Files:
{', '.join(files)}

Summary:
{memory.get('summary', '')}

Solution:
{memory.get('solution', '')}

-------------------
"""

    prompt = f"""
You are analyzing debugging memories.

Identify:

1. Repeated causes of failure.
2. Repeated solution strategies.
3. Recurring mistakes.
4. Practices that prevent bugs.

Return ONLY bullet points.

No introduction.
No explanations.
No conversational language.

Memories:

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