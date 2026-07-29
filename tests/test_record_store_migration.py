"""The durable store must migrate legacy Chroma records and rebuild an index."""

import os
import tempfile

database = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3").name
os.unlink(database)
os.environ["MEMCODER_RECORD_DB_PATH"] = database

from memory.record_store import (
    list_records,
    migrate_legacy_chroma,
    rebuild_guidance_index,
)


class FakeCollection:
    def __init__(self):
        self.records = {
            "legacy-id": {
                "metadata": {
                    "hash": "legacy-id",
                    "task": "Validate project name",
                    "files": ["project.py"],
                    "summary": "Missing names need validation.",
                    "solution": "Reject missing values.",
                    "type": "experience",
                    "owner": "migration-test",
                    "timestamp": "2026-01-01T00:00:00+00:00",
                },
                "document": "legacy document",
            }
        }

    def get(self, ids=None, include=None):
        selected = self.records if ids is None else {
            record_id: self.records[record_id]
            for record_id in ids if record_id in self.records
        }
        return {
            "ids": list(selected),
            "metadatas": [record["metadata"] for record in selected.values()],
            "documents": [record["document"] for record in selected.values()],
        }

    def delete(self, ids):
        for record_id in ids:
            self.records.pop(record_id, None)

    def add(self, ids, documents, embeddings, metadatas):
        for record_id, document, metadata in zip(ids, documents, metadatas):
            self.records[record_id] = {"document": document, "metadata": metadata}


collection = FakeCollection()
migration = migrate_legacy_chroma(collection)
assert migration == {"migrated": 1, "already_migrated": False}
assert migrate_legacy_chroma(collection)["already_migrated"]

records = list_records()
assert len(records) == 1
assert records[0]["record_id"] == "legacy-id"
assert records[0]["record_state"] == "trusted"

rebuilt = rebuild_guidance_index(collection, embed=lambda text: [float(len(text))])
assert rebuilt["indexed"] == 1
assert list(collection.records) == ["legacy-id"]
assert collection.records["legacy-id"]["metadata"]["record_id"] == "legacy-id"

print("PASS: durable record migration and index rebuild")
