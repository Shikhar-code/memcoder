from memcoder import (
    MemCoderAgent,
    banner,
    show_results,
    show_answer
)

coder = MemCoderAgent.coder()

coder.clear()

conversation = """
User:

torch.cuda.is_available() returns False.

Assistant:

Install the CUDA-enabled PyTorch build.
"""

banner("Learning")

coder.learn(conversation)

banner("Searching")

show_results(
    coder.search("cuda")
)

banner("Solving")

show_answer(
    coder.solve(
        "My RTX 4090 is not detected by PyTorch."
    )
)

coder.clear()

print("\nExample completed successfully.")