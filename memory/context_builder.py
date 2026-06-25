from memory.search import search_memory
from memory.context_formatter import format_context
from memory.compressor import compress_memories
from memory.memory_budget import budget_memories
from memory.problem_builder import build_problem_description

from llm.rerank_llm import rerank_memories


def build_context(task):

    # Retrieve memories
    experiences = search_memory(
        task,
        k=20,
        memory_type="experience"
    )

    reflections = search_memory(
        task,
        k=5,
        memory_type="reflection"
    )

    principles = search_memory(
        task,
        k=5,
        memory_type="principle"
    )

    mistakes = search_memory(
        task,
        k=5,
        memory_type="mistake"
    )

    # Budget each category
    experiences = budget_memories(
        experiences,
        query=task,
        max_memories=10
    )

    reflections = budget_memories(
        reflections,
        query=task,
        max_memories=2
    )

    principles = budget_memories(
        principles,
        query=task,
        max_memories=3
    )

    mistakes = budget_memories(
        mistakes,
        query=task,
        max_memories=3
    )

    # Build richer problem description
    problem_description = build_problem_description(
        task
    )
    if verbose:
    # Debug before rerank
        print("\n===== BEFORE RERANK =====")

        for i, memory in enumerate(experiences, start=1):
            print(i, memory["task"])

    # LLM rerank
    experiences = rerank_memories(
        problem_description,
        experiences
    )
    if verbose:
    # Debug after rerank
        print("\n===== AFTER RERANK =====")

        for i, memory in enumerate(experiences, start=1):
            print(i, memory["task"])

    # Merge memories
    memories = (
        experiences
        + reflections
        + principles
        + mistakes
    )

    # Format
    context = format_context(
        memories,
        task
    )

    context += "\n"

    context += compress_memories(
        experiences
    )

    return context