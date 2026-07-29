from memory.embedder import embed
from memory.chroma_client import collection
from memory.duplicate import find_duplicate
from memory.importance import score_importance
from memory.confidence import confidence_score
from memory.records import initialize_record, searchable_document
from memory.record_store import (
    migrate_legacy_chroma,
    migrate_legacy_workspace_storage,
    save_record,
)



def add_memory(
        memory,
        verbose=False):

    # Move existing Chroma-only records into the durable store once before
    # admitting a new record. Chroma remains a rebuildable retrieval index.
    migrate_legacy_workspace_storage()
    migrate_legacy_chroma(collection)

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

    if "importance" not in memory:

        memory["importance"] = score_importance(
            memory
        )

    if "type" not in memory:

        memory["type"] = "experience"

    if "owner" not in memory:

        memory["owner"] = "shared"

    memory["confidence"] = confidence_score(memory)
    initialize_record(memory)

    # -------------------------
    # Duplicate check
    # -------------------------

    duplicate = find_duplicate(memory)

    if duplicate:

        if verbose:
            print("Memory already exists. Skipping.")

        return duplicate

    # -------------------------
    # Build searchable document
    # -------------------------

    text = searchable_document(memory)

    # -------------------------
    # Persist source of truth before indexing
    # -------------------------

    save_record(memory, document=text)

    # -------------------------
    # Store
    # -------------------------

    collection.add(

        ids=[
        memory["record_id"]
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
