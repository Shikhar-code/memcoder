def solve_and_learn(
        user_prompt,
        session_context="",
        agent_id="human",
        solved=True,
        verbose=False):

    from agent.problem_solver import solve_problem
    from memory.conversation_learner import learn_from_conversation

    result = solve_problem(
        user_prompt,
        session_context=session_context,
        agent_id=agent_id,
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
            conversation,
            agent_id=agent_id
        )

        result["learned_memory"] = memory

    return result
