from llm.optional_ollama import get_ollama
import re


def rerank_memories(problem_description, memories, verbose=False):

    prompt = f"""
Current problem:

{problem_description}

Candidate memories:

"""

    for i, memory in enumerate(memories, start=1):

        prompt += f"""
{i}

Task:
{memory['task']}

Summary:
{memory['summary']}

------------------------
"""

    prompt += """

Choose the FIVE memories MOST useful.

Prioritize:

1. Same framework.
2. Same subsystem.
3. Same files.
4. Same failure mode.
5. Same technology stack.

Examples:

Remotion render crashes should prefer:

- WebGL issues
- headless rendering issues
- composition problems
- video rendering problems
- React rendering problems

Avoid:

- kernel crashes
- operating system bugs
- networking issues

Return ONLY numbers.

Example:

1
7
3
5
9

No explanation.
"""

    response = get_ollama().chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        think=False,
        options={
            "temperature": 0,
            "num_predict": 20
        }
    )

    text = response.message.content
    if verbose:
        print("\n===== RERANKER RAW OUTPUT =====")
        print(text)
        print("===============================\n")

    numbers = re.findall(r"\d+", text)

    indices = []

    for n in numbers:

        idx = int(n) - 1

        if 0 <= idx < len(memories):
            indices.append(idx)

    indices = list(dict.fromkeys(indices))
    if verbose:
        print("Parsed indices:", indices)

    if len(indices) == 0:
        if verbose:

            print("FALLING BACK TO FIRST 5")

        return memories[:5]

    return [memories[i] for i in indices[:5]]
