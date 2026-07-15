from memory.embedder import embed
from memory.chroma_client import collection
from memory.duplicate import is_duplicate
from memory.memory_hash import memory_hash
from memory.importance import score_importance
from memory.confidence import confidence_score



def add_memory(
        memory,
        verbose=False):

    # -------------------------
    # Defensive defaults
    # -------------------------

    if not memory.get("files"):
        memory["files"] = ["unknown"]

    if not memory.get("summary"):
        memory["summary"] = ""

    if not memory.get("solution"):
        memory["solution"] = "Unknown"

    if not memory.get("verification"):
        memory["verification"] = ""

    # -------------------------
    # Metadata
    # -------------------------

    memory["confidence"] = confidence_score(
        memory
    )

    memory["hash"] = memory_hash(
        memory
    )

    if "importance" not in memory:

        memory["importance"] = score_importance(
            memory
        )

    if "type" not in memory:

        memory["type"] = "experience"

    if "owner" not in memory:

        memory["owner"] = "shared"

    # -------------------------
    # Duplicate check
    # -------------------------

    if is_duplicate(memory):

        if verbose:
            print("Memory already exists. Skipping.")

        return memory

    # -------------------------
    # Build searchable document
    # -------------------------

    text = f"""
Task:
{memory['task']}

Files:
{', '.join(memory['files'])}

Summary:
{memory['summary']}

Solution:
{memory['solution']}
"""

    # -------------------------
    # Store
    # -------------------------

    collection.add(

        ids=[
        memory["hash"]
        ],

        documents=[
            text
        ],

        embeddings=[
            embed(text)
        ],

        metadatas=[
            memory
        ]

    )

    if verbose:
        print("Memory added.")

    return memory
