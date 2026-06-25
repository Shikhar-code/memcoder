import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from client import MemCoderAgent
from memory.capture import capture_memory
from memory.chroma_client import collection


# =====================================================
# Helpers
# =====================================================

def check(condition, name):

    if condition:

        print(f"[PASS] {name}")

    else:

        print(f"[FAIL] {name}")

        raise Exception(name)


def find_memory(results, task):

    for memory in results:

        if memory["task"].lower() == task.lower():

            return memory

    return None


print()
print("=" * 60)
print("MemCoder Alpha Integration Test")
print("=" * 60)
print()

tester = MemCoderAgent("alpha_test")
observer = MemCoderAgent("alpha_observer")

TASK = "Alpha CRUD Memory"


# =====================================================
# TEST 1
# Learn pipeline
# =====================================================

print("Testing learn pipeline...")

before = len(collection.get()["ids"])

tester.learn(
"""
User problem:

My Docker container exits immediately.

MemCoder answer:

Run the application in the foreground.
"""
)

after = len(collection.get()["ids"])

check(

    after >= before,

    "Learn Pipeline"

)


# =====================================================
# TEST 2
# Deterministic CRUD
# =====================================================

print()

print("Creating deterministic memory...")

capture_memory(

    task=TASK,

    files=["alpha.py"],

    summary="Initial summary.",

    solution="Initial solution.",

    importance=5,

    memory_type="experience",

    owner="alpha_test"

)


# =====================================================
# SEARCH
# =====================================================

results = tester.search(

    TASK,

    k=10

)

memory = find_memory(

    results,

    TASK

)

check(

    memory is not None,

    "Search"

)


# =====================================================
# PRIVATE OWNERSHIP
# =====================================================

results = observer.search(

    TASK,

    k=10

)

memory = find_memory(

    results,

    TASK

)

check(

    memory is None,

    "Private Ownership"

)


# =====================================================
# UPDATE
# =====================================================

memory = find_memory(

    tester.search(
        TASK,
        k=10
    ),

    TASK

)

tester.update(

    memory["id"],

    summary="Updated summary."

)

memory = find_memory(

    tester.search(
        TASK,
        k=10
    ),

    TASK

)

check(

    memory is not None

    and

    memory["summary"] == "Updated summary.",

    "Update"

)


# =====================================================
# SHARE
# =====================================================

tester.share(

    memory["id"]

)

memory = find_memory(

    observer.search(
        TASK,
        k=10
    ),

    TASK

)

check(

    memory is not None,

    "Share"

)


# =====================================================
# TRANSFER
# =====================================================

observer.transfer(

    memory["id"],

    "alpha_observer"

)

memory = find_memory(

    tester.search(
        TASK,
        k=10
    ),

    TASK

)

check(

    memory is None,

    "Transfer Removed"

)

memory = find_memory(

    observer.search(
        TASK,
        k=10
    ),

    TASK

)

check(

    memory is not None,

    "Transfer Added"

)


# =====================================================
# DELETE
# =====================================================

observer.delete(

    memory["id"]

)

memory = find_memory(

    observer.search(
        TASK,
        k=10
    ),

    TASK

)

check(

    memory is None,

    "Delete"

)


# =====================================================
# SESSION
# =====================================================

session = tester.session()

session.solve(

    "Redis cache misses."

)

session.solve(

    "I already flushed Redis."

)

check(

    len(session.history) == 2,

    "Session"

)


print()
print("=" * 60)
print("ALL MEMCODER ALPHA TESTS PASSED")
print("=" * 60)