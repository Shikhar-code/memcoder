import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from memory.chroma_client import collection
from memory.memory_hash import memory_hash
from memory.confidence import confidence_score
from memory.importance import score_importance
from memory.embedder import embed


TEST_OWNERS = {

    "alpha_test",
    "alpha_observer"

}

TEST_TASKS = {

    "duplicate test",
    "duplicate architecture test",
    "coder memory",
    "research memory",
    "shared memory"

}


print()
print("=" * 60)
print("MemCoder Cleanup")
print("=" * 60)
print()

results = collection.get(
    include=[
        "metadatas",
        "documents",
        "embeddings"
    ]
)

ids = results["ids"]
documents = results["documents"]
metadatas = results["metadatas"]

seen_hashes = set()

duplicates_removed = 0
metadata_repaired = 0
test_deleted = 0


for memory_id, document, memory in zip(

    ids,

    documents,

    metadatas

):

    # ---------------------------------------
    # Delete temporary testing memories
    # ---------------------------------------

    if (

        memory.get("owner") in TEST_OWNERS

        or

        memory.get(
            "task",
            ""
        ).lower() in TEST_TASKS

    ):

        collection.delete(
            ids=[memory_id]
        )

        test_deleted += 1

        continue

    # ---------------------------------------
    # Duplicate detection
    # ---------------------------------------

    h = memory_hash(
        memory
    )

    if h in seen_hashes:

        collection.delete(
            ids=[memory_id]
        )

        duplicates_removed += 1

        continue

    seen_hashes.add(h)

    repaired = False

    # ---------------------------------------
    # Repair owner
    # ---------------------------------------

    if "owner" not in memory:

        memory["owner"] = "shared"

        repaired = True

    # ---------------------------------------
    # Repair confidence
    # ---------------------------------------

    if "confidence" not in memory:

        memory["confidence"] = confidence_score(
            memory
        )

        repaired = True

    # ---------------------------------------
    # Repair importance
    # ---------------------------------------

    if "importance" not in memory:

        memory["importance"] = score_importance(
            memory
        )

        repaired = True

    # ---------------------------------------
    # Repair type
    # ---------------------------------------

    if "type" not in memory:

        memory["type"] = "experience"

        repaired = True

    # ---------------------------------------
    # Repair hash
    # ---------------------------------------

    new_hash = memory_hash(
        memory
    )

    if (

        memory.get("hash") != new_hash

        or

        memory_id != new_hash

    ):

        memory["hash"] = new_hash

        collection.delete(
            ids=[memory_id]
        )

        collection.add(

            ids=[
                new_hash
            ],

            documents=[
                document
            ],

            embeddings=[
                embed(
                    document
                )
            ],

            metadatas=[
                memory
            ]

        )

        repaired = True

    if repaired:

        metadata_repaired += 1


print()

print("=" * 60)

print("Cleanup Complete")

print("=" * 60)

print()

print(

    f"Duplicates removed : {duplicates_removed}"

)

print(

    f"Metadata repaired  : {metadata_repaired}"

)

print(

    f"Test memories deleted : {test_deleted}"

)

print()

print(

    f"Remaining memories : {collection.count()}"

)

print()

print("=" * 60)