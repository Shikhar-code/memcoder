from memcoder import (
    MemCoderAgent,
    banner,
    show_answer
)

coder = MemCoderAgent.coder()

coder.clear()

session = coder.session()

banner("Conversation")

show_answer(

    session.solve(
        "My PostgreSQL server won't start."
    )

)

show_answer(

    session.solve(
        "I already checked the logs."
    )

)

banner("History")

for i, turn in enumerate(session.history, 1):

    print(f"Turn {i}")

    print("-" * 50)

    print("User")

    print(turn["user"])

    print()

    print("Assistant")

    print(turn["assistant"])

    print()

coder.clear()

print("\nExample completed successfully.")