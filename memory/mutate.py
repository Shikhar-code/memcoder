from memory.chroma_client import collection
from memory.embedder import embed
from memory.records import record_id, revise_record, searchable_document
from memory.record_store import save_record


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

    revise_record(memory)
    document = searchable_document(memory)

    # SQLite is authoritative; the index update below is rebuildable.
    save_record(memory, document=document)

    # -----------------------
    # Replace record
    # -----------------------

    # Updating in place prevents a mutable edit from breaking provenance links.
    collection.update(
        ids=[memory_id],
        documents=[document],
        embeddings=[embed(document)],
        metadatas=[memory],
    )

    memory["id"] = record_id(memory)

    return memory
