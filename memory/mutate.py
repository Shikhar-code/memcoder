from memory.chroma_client import collection
from memory.embedder import embed
from memory.memory_hash import memory_hash


def mutate_memory(
        memory_id,
        mutation):

    results = collection.get(

        ids=[memory_id],

        include=[
            "metadatas",
            "documents",
            "embeddings"
        ]

    )

    if len(results["ids"]) == 0:

        return None

    memory = results["metadatas"][0]

    document = results["documents"][0]

    # -----------------------
    # Apply mutation
    # -----------------------

    mutation(
        memory
    )

    # -----------------------
    # Recompute hash
    # -----------------------

    memory["hash"] = memory_hash(
        memory
    )

    document = f"""
Task:
{memory['task']}

Files:
{', '.join(memory['files'])}

Summary:
{memory['summary']}

Solution:
{memory['solution']}
"""

    # -----------------------
    # Replace record
    # -----------------------

    collection.delete(
        ids=[memory_id]
    )

    collection.add(

        ids=[
            memory["hash"]
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

    memory["id"] = memory["hash"]

    return memory