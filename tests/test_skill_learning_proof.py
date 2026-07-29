"""Beta 2 proof: verified outcomes can alter guidance for a related later task."""

import importlib
import json
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))


records = {
    "experience-1": {
        "type": "experience",
        "owner": "proof-agent",
        "verification": json.dumps({"qa_verdict": "approved"}),
    },
    "experience-2": {
        "type": "experience",
        "owner": "proof-agent",
        "verification": json.dumps({"qa_verdict": "approved"}),
    },
}


class FakeCollection:
    def get(self, ids, include):
        return {
            "ids": [record_id for record_id in ids if record_id in records],
            "metadatas": [records[record_id] for record_id in ids if record_id in records],
        }


chroma = types.ModuleType("memory.chroma_client")
chroma.collection = FakeCollection()
sys.modules["memory.chroma_client"] = chroma

stored = []
store = types.ModuleType("memory.store")


def add_memory(memory):
    memory["hash"] = "skill-required-field-validation"
    stored.append(memory)
    return memory


store.add_memory = add_memory
sys.modules["memory.store"] = store

provenance = types.ModuleType("memory.provenance")
provenance.link = lambda *args, **kwargs: None
sys.modules["memory.provenance"] = provenance

from memory.skills import promote_skill


skill = promote_skill(
    name="Required field validation",
    when_to_use="A request can omit a required field before string processing.",
    inputs=["request payload", "field name"],
    steps=[
        "Check the required field before accessing it.",
        "Raise the expected validation error when it is absent.",
    ],
    verification=["Run the focused validation test."],
    supporting_experience_ids=["experience-1", "experience-2"],
    agent_id="proof-agent",
)

assert skill["promoted"]
promoted_memory = stored[0]
promoted_memory["id"] = skill["id"]

search = types.ModuleType("memory.hierarchical_search")


def hierarchical_search(problem, agent_id, include_shared=True):
    assert "customer_id" in problem
    assert agent_id == "proof-agent"
    assert include_shared is False
    return {
        "confidence": 0.88,
        "strategy": "memory_first",
        "skills": [promoted_memory],
        "experiences": [],
        "mistakes": [],
        "principles": [],
        "reflections": [],
    }


search.hierarchical_search = hierarchical_search
sys.modules["memory.hierarchical_search"] = search
sys.modules.pop("api.cognition", None)
cognition = importlib.import_module("api.cognition")

started = cognition.start_cognition(
    "Reject requests that omit customer_id before processing.",
    agent_id="proof-agent",
    include_shared=False,
)

assert started["brief"]["evidence"][0]["type"] == "skill"
assert started["plan"]["mode"] == "skill_guided"
assert started["plan"]["source_skill"]["id"] == "skill-required-field-validation"
assert started["plan"]["steps"][0]["action"] == (
    "Check the required field before accessing it."
)
assert started["plan"]["steps"][-1]["verification"] == [
    "Run the focused validation test."
]

print("PASS: QA-approved experience changes later task guidance")
