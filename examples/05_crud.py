from memcoder import (
    MemCoderAgent,
    banner,
    show
)

from memory.capture import capture_memory

coder = MemCoderAgent.coder()

coder.clear()

capture_memory(

    task="Redis cache misses",

    files=["redis.py"],

    summary="Redis selected the wrong database.",

    solution="Use the correct Redis database.",

    owner="coder"

)

memory = coder.search_one(
    "redis"
)

banner("Created")

show(memory)

coder.update(

    memory["id"],

    summary="Redis selected the wrong logical database."

)

memory = coder.search_one(
    "redis"
)

banner("Updated")

show(memory)

coder.share(
    memory["id"]
)

banner("Shared")

show(memory)

coder.delete(
    memory["id"]
)

coder.clear()

print("\nMemory deleted.")

print("\nExample completed successfully.")