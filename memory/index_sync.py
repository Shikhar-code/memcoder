"""Keep Chroma's rebuildable retrieval index aligned with durable records."""

from memory.chroma_client import collection
from memory.embedder import embed
from memory.records import record_id, searchable_document


def sync_record(memory):
    document = searchable_document(memory)
    identifier = record_id(memory)
    existing = collection.get(ids=[identifier])
    method = collection.update if existing.get("ids") else collection.add
    method(
        ids=[identifier],
        documents=[document],
        embeddings=[embed(document)],
        metadatas=[memory],
    )
    return identifier
