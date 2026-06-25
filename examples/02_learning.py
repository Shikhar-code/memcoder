from memcoder import (
    MemCoderAgent,
    banner,
    show_trace
)

coder = MemCoderAgent.coder()

coder.clear()

conversation = """
User:

My Docker container exits immediately.

Assistant:

Run the application in the foreground.
"""

banner("Learning")

print(
    coder.learn(
        conversation
    )
)

banner("Trace")

show_trace(

    coder.trace(
        "docker container exits immediately"
    )

)

coder.clear()

print("\nExample completed successfully.")