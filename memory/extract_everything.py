from llm.optional_ollama import get_ollama


def extract_everything(conversation):

    prompt = f"""
Read the coding conversation and extract:

1. One experience.
2. Reflections (observations).
3. Principles (general reusable rules).
4. Debugging mistakes.

Do NOT copy example text.
Use actual information from the conversation.

Output format:

EXPERIENCE

TASK:
<actual task>

FILES:
<comma separated files>

SUMMARY:
<actual summary>

SOLUTION:
<actual solution>

-------------------

REFLECTIONS

Extract at most TWO reflections.

A reflection is a pattern about HOW the problem was approached.

Reflections should describe:

- wrong assumptions
- debugging habits
- mistakes in reasoning
- patterns in how debugging was performed

Do NOT output:

- technical solutions
- lists
- causes of failures
- fixes
- programming advice
- facts already present in experiences
- facts already present in principles
- multiple sentences
- paragraphs

Each reflection must:

- be one sentence
- be under 20 words
- begin with "I"
Reflections are about the debugger, not about the software.

They should describe how the investigation happened, not how the bug works.

Good examples:

1. I assumed the output was missing before inspecting the response object.
2. I debugged symptoms before validating configuration.

Bad examples:

1. Causes of packet drops.
2. Lock contention issues.
3. General programming advice.

Output:

1. <reflection>
2. <reflection>
-------------------

PRINCIPLES

1. <actual principle>
2. <actual principle>

-------------------

MISTAKES

TASK:
<actual mistake>

FILES:
<files>

SUMMARY:
<summary>

SOLUTION:
<solution>

TASK:
<actual mistake>

FILES:
<files>

SUMMARY:
<summary>

SOLUTION:
<solution>

Important rules:

- Never output placeholders.
- Never output "Describe the problem".
- Never output "...".
- Replace every field with actual content.
- If something is unknown, write "unknown".
- Output only the format above.

Conversation:

{conversation}
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
            "temperature": 0
        }
    )

    return response.message.content
