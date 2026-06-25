import json
import ollama


def extract_memory_llm(conversation):

    prompt = f"""
You are extracting software debugging memories.

Example:

Conversation:

Scene10 render crashed.

Root cause:
durationInFrames became zero.

composition.tsx had duration hardcoded.

Fixed by validating duration before registering composition.

JSON:

{{
"task":"durationInFrames became zero",
"files":["composition.tsx"],
"summary":"Composition duration became zero because duration was hardcoded.",
"solution":"Validate duration before registering composition."
}}

--------------------------------

Conversation:

TensorFlow could not detect the RTX 3050.

training.ipynb was using incompatible CUDA versions.

Installed GPU-compatible TensorFlow and CUDA.

JSON:

{{
"task":"TensorFlow GPU not detected",
"files":["training.ipynb"],
"summary":"TensorFlow failed to detect RTX 3050 because of CUDA incompatibility.",
"solution":"Install GPU-compatible TensorFlow and CUDA."
}}

--------------------------------

Conversation:

{conversation}

JSON:
"""

    response = ollama.chat(
        model="qwen2.5-coder:3b",
        think=False,
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return json.loads(
        response["message"]["content"]
    )