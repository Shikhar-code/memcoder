"""Guidance storage keeps stable IDs when mutable content is revised."""

import os
import tempfile

database = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3").name
os.unlink(database)
os.environ["MEMCODER_RECORD_DB_PATH"] = database

from memory import duplicate, mutate, store


class FakeCollection:
    def __init__(self):
        self.records = {}

    def get(self, ids=None, where=None, include=None):
        if ids is not None:
            found = [(record_id, self.records[record_id]) for record_id in ids if record_id in self.records]
        else:
            clauses = where.get("$and", []) if where else []
            expected = {
                key: value
                for clause in clauses
                for key, value in clause.items()
            }
            found = [
                (record_id, record)
                for record_id, record in self.records.items()
                if all(record["metadata"].get(key) == value for key, value in expected.items())
            ]
        return {
            "ids": [record_id for record_id, _ in found],
            "metadatas": [record["metadata"] for _, record in found],
            "documents": [record["document"] for _, record in found],
            "embeddings": [record["embedding"] for _, record in found],
        }

    def add(self, ids, documents, embeddings, metadatas):
        for record_id, document, embedding, metadata in zip(ids, documents, embeddings, metadatas):
            self.records[record_id] = {
                "document": document,
                "embedding": embedding,
                "metadata": metadata,
            }

    def update(self, ids, documents, embeddings, metadatas):
        self.add(ids, documents, embeddings, metadatas)


collection = FakeCollection()
store.collection = collection
duplicate.collection = collection
mutate.collection = collection
store.embed = lambda text: [float(len(text))]
mutate.embed = lambda text: [float(len(text))]

stored = store.add_memory({
    "task": "Validate required project name",
    "files": ["project.py"],
    "summary": "A name is required before normalization.",
    "solution": "Reject missing and blank values.",
    "type": "experience",
    "owner": "lifecycle-test",
})
record_id = stored["record_id"]
original_hash = stored["content_hash"]
assert list(collection.records) == [record_id]

updated = mutate.mutate_memory(
    record_id,
    lambda memory: memory.update({"solution": "Reject missing, null, and blank values."}),
)

assert updated["id"] == record_id
assert updated["revision"] == 2
assert updated["content_hash"] != original_hash
assert list(collection.records) == [record_id]
assert collection.records[record_id]["metadata"]["record_id"] == record_id

print("PASS: guidance storage preserves stable IDs across revisions")
