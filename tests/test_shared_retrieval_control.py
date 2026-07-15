"""Ensure controlled evaluations can exclude globally shared memories."""

import importlib
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))


class FakeCollection:
    def __init__(self):
        self.where = None

    def query(self, **kwargs):
        self.where = kwargs["where"]
        return {"metadatas": [[]], "distances": [[]]}


collection = FakeCollection()
chroma = types.ModuleType("memory.chroma_client")
chroma.collection = collection
sys.modules["memory.chroma_client"] = chroma

embedder = types.ModuleType("memory.embedder")
embedder.embed = lambda query: [0.0]
sys.modules["memory.embedder"] = embedder

sys.modules.pop("memory.search", None)
search = importlib.import_module("memory.search")

search.search_memory(
    query="required field",
    memory_type="experience",
    agent_id="proof-owner",
    include_shared=False
)

assert collection.where == {
    "$and": [
        {"type": "experience"},
        {"owner": "proof-owner"}
    ]
}

print("PASS: shared retrieval can be excluded")
