"""A verified outcome must create inspectable evidence links automatically."""

import os
import tempfile

record_database = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3").name
audit_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl").name
os.unlink(record_database)
os.unlink(audit_path)
os.environ["MEMCODER_RECORD_DB_PATH"] = record_database
os.environ["MEMCODER_AUDIT_PATH"] = audit_path

from memory import duplicate, store
from memory.provenance import trace
from memory.record_outcome import record_outcome


class FakeCollection:
    def __init__(self):
        self.records = {}

    def get(self, ids=None, where=None, include=None):
        if ids is not None:
            selected = {
                record_id: self.records[record_id]
                for record_id in ids if record_id in self.records
            }
        elif where:
            clauses = where.get("$and", [])
            expected = {key: value for clause in clauses for key, value in clause.items()}
            selected = {
                record_id: record for record_id, record in self.records.items()
                if all(record["metadata"].get(key) == value for key, value in expected.items())
            }
        else:
            selected = self.records
        return {
            "ids": list(selected),
            "metadatas": [record["metadata"] for record in selected.values()],
            "documents": [record["document"] for record in selected.values()],
        }

    def add(self, ids, documents, embeddings, metadatas):
        for record_id, document, metadata in zip(ids, documents, metadatas):
            self.records[record_id] = {"document": document, "metadata": metadata}


collection = FakeCollection()
store.collection = collection
duplicate.collection = collection
store.embed = lambda text: [float(len(text))]

result = record_outcome(
    task="Validate a required project name",
    files=["project.py"],
    summary="The focused test proved a missing project name caused a KeyError.",
    solution="Validate missing and blank names before normalizing the value.",
    reflection="I checked the missing-name path before validating input.",
    principles=["Validate required input before normalizing string values."],
    agent_id="provenance-flow",
    plan_id="plan_1234567890abcdef1234",
    qa_report={"verdict": "approved", "schema_version": 1, "evidence_summary": {}},
)

experience_id = result["experience"]["id"]
experience_edges = trace(experience_id, owner="provenance-flow")
assert {(edge["relation"], edge["direction"]) for edge in experience_edges} == {
    ("derived_from", "incoming"),
    ("derived_from", "incoming"),
    ("validated_by", "outgoing"),
}
assert result["plan_outcome"]["id"] in {edge["target_id"] for edge in experience_edges}

print("PASS: verified outcome automatically creates provenance links")
