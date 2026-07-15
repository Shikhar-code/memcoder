from memory.problem_builder import build_problem_description
from memory.hierarchical_search import hierarchical_search
from context.hierarchical_context_builder import (
    build_hierarchical_context
)

from llm.optional_ollama import get_ollama
import time


def solve_problem(
        user_prompt,
        session_context="",
        agent_id="human",
        verbose=False):

    total_start = time.time()

    if is_ambiguous(user_prompt):

        if session_context.strip() == "":

            return {

                "answer":
                "I don't currently have enough context. Could you clarify what you're referring to?",

                "used_memories": []

            }

    # Build retrieval query
    retrieval_query_start = time.time()

    retrieval_problem = build_problem_description(
        task=user_prompt
    )

    retrieval_query_time = (
        time.time()
        - retrieval_query_start
    )

    # Retrieve memories
    search_start = time.time()

    results = hierarchical_search(
        retrieval_problem,
        agent_id=agent_id
    )

    search_time = (
        time.time()
        - search_start
    )

    total_memories = (
        len(results["experiences"])
        + len(results["mistakes"])
        + len(results["principles"])
        + len(results["reflections"])
    )

    # Build memory context
    context_start = time.time()

    memory_context = build_hierarchical_context(
        results,
        query=retrieval_problem
    )

    if total_memories == 0:

        memory_context = """
No relevant memories were found.

Solve the problem normally.

If the user's problem is unclear or meaningless, say so instead of inventing an answer.
"""

    context_time = (
        time.time()
        - context_start
    )

    # Final prompt
    prompt = f"""
You are MemCoder.

Conversation history:

{session_context}

Current problem:

{user_prompt}

Relevant memories:

{memory_context}

Instructions:

1. Use memories when relevant.
2. Avoid repeating known mistakes.
3. Ignore irrelevant memories.
4. Prefer specific experiences.
5. Use session history to resolve references like "it" or "that".
6. Do not blindly trust memories.
7. If memories conflict, prefer the most specific.
8. If no memories are relevant, solve the problem normally.
9. If the problem is absurd, contradictory, metaphorical, fictional, or lacks enough information, explicitly say so instead of inventing a technical explanation.
10. Do not assume fictional scenarios are real.
11. Be concise and practical.
12. Treat observations as process guidance: use them to choose the first verification step, never as proof of root cause.

Output sections:

1. Root Cause
2. Reasoning
3. Concrete Steps
4. Verification

Answer:
"""

    if verbose:

        print("\n========== USER PROBLEM ==========\n")
        print(user_prompt)

        print("\n========== RETRIEVAL QUERY ==========\n")
        print(retrieval_problem)

        print("\n========== EXPERIENCES ==========\n")
        for memory in results["experiences"]:
            print(memory["task"], "| score:", round(memory["score"], 3))

        print("\n========== MISTAKES ==========\n")
        for memory in results["mistakes"]:
            print(memory["task"], "| score:", round(memory["score"], 3))

        print("\n========== PRINCIPLES ==========\n")
        for memory in results["principles"]:
            print(memory["task"], "| score:", round(memory["score"], 3))

        print("\n========== REFLECTIONS ==========\n")
        for memory in results["reflections"]:
            print(memory["summary"], "| score:", round(memory["score"], 3))

        print("\n========== MEMORY CONTEXT ==========\n")
        print(memory_context)

        print("\n========== FINAL PROMPT ==========\n")
        print(prompt)

    llm_start = time.time()

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

    answer = response.message.content

    llm_time = (
        time.time()
        - llm_start
    )

    total_time = (
        time.time()
        - total_start
    )

    if verbose:

        print("\n========== ANSWER ==========\n")
        print(answer)

        print()

        print(
            f"Retrieval query : {retrieval_query_time:.2f}s"
        )

        print(
            f"Search          : {search_time:.2f}s"
        )

        print(
            f"Context build   : {context_time:.2f}s"
        )

        print(
            f"LLM             : {llm_time:.2f}s"
        )

        print(
            f"Total solve     : {total_time:.2f}s"
        )

    return {

        "problem": user_prompt,

        "retrieval_problem": retrieval_problem,

        "retrieval": results,

        "memory_context": memory_context,

        "prompt": prompt,

        "answer": answer,

        "raw_response": response,

        "timings": {

            "retrieval_query":
                retrieval_query_time,

            "search":
                search_time,

            "context":
                context_time,

            "llm":
                llm_time,

            "total":
                total_time

        }

    }


def is_ambiguous(query):

    pronouns = {

        "it",
        "that",
        "this",
        "they",
        "them",
        "those",
        "he",
        "she",
        "these",
        "there"

    }

    words = query.lower().split()

    if len(words) <= 7:

        for word in words:

            if word in pronouns:

                return True

    return False
