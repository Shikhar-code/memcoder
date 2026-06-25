from memcoder import (
    MemCoderAgent,
    banner,
    show_results
)

coder = MemCoderAgent.coder()
research = MemCoderAgent.research()

coder.clear()
research.clear()

conversation = """
User:

Vector search is becoming slow.

Assistant:

Approximate Nearest Neighbor indexing
greatly improves retrieval speed.
"""

banner("Coder Learning")

coder.learn(
    conversation
)

banner("Coder Memories")

results = coder.search(
    "vector search"
)

show_results(results)

memory = coder.search_one(
    "vector search"
)

banner("Sharing")

coder.share(
    memory["id"]
)

banner("Research Agent")

show_results(

    research.search(
        "vector search"
    )

)

coder.clear()
research.clear()

print("\nExample completed successfully.")