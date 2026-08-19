import os

from memory.embedder import embed
import memory.embedder as embedder_module
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

    from memory.policy import PolicyDenied, evaluate_admission

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

    admission = evaluate_admission(
        files=memory.get("files"),
        text=[memory.get("task"), memory.get("summary"), memory.get("solution"), memory.get("verification")],
        owner=memory.get("owner"),
    )
    if not admission["allowed"]:
        raise PolicyDenied(admission["explanation"])

    # Persistent hosts prewarm the rebuildable semantic index. One-shot and
    # offline hosts admit into the durable lexical store immediately instead
    # of loading a model or opening Chroma just to record verified work.
    warm_check = getattr(embedder_module, "is_warm", None)
    semantic_enabled = collection.__class__.__name__ != "ChromaCollectionProxy" or (
        bool(warm_check()) if warm_check else True
    ) or os.environ.get("MEMCODER_ALLOW_COLD_SEMANTIC", "").lower() in {
        "1", "true", "yes"
    }
    if semantic_enabled:
        migrate_legacy_workspace_storage()
        migrate_legacy_chroma(collection)

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

    if not semantic_enabled:
        return memory

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
