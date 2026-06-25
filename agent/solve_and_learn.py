from agent.problem_solver import solve_problem
from memory.conversation_learner import (
    learn_from_conversation
)


def solve_and_learn(
        user_prompt,
        solved=True,
        verbose=False):

    result = solve_problem(
        user_prompt,
        verbose=verbose
    )

    answer = result["answer"]

    if solved:

        conversation = f"""
User problem:

{user_prompt}

MemCoder answer:

{answer}
"""

        memory = learn_from_conversation(
            conversation
        )

        result["learned_memory"] = memory

    return result