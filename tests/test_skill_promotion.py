"""Skills must have QA-approved, accessible supporting experience evidence."""

import json
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))


def experience(owner="skill-test", approved=True):
    return {
        "type": "experience",
        "owner": owner,
        "verification": json.dumps({"qa_verdict": "approved" if approved else "rejected"}),
    }


records = {
    "experience-1": experience(),
    "experience-2": experience(),
    "experience-bad": experience(approved=False),
    "principle-1": {
        "type": "principle",
        "owner": "skill-test",
        "verification": "",
    },
}


class FakeCollection:
    def get(self, ids, include):
        return {
            "ids": [memory_id for memory_id in ids if memory_id in records],
            "metadatas": [records[memory_id] for memory_id in ids if memory_id in records],
        }


chroma = types.ModuleType("memory.chroma_client")
chroma.collection = FakeCollection()
sys.modules["memory.chroma_client"] = chroma

stored = []
store = types.ModuleType("memory.store")


def add_memory(memory):
    memory["hash"] = "skill-1"
    stored.append(memory)
    return memory


store.add_memory = add_memory
sys.modules["memory.store"] = store

links = []
provenance = types.ModuleType("memory.provenance")
provenance.link = lambda *args, **kwargs: links.append(args)
sys.modules["memory.provenance"] = provenance

from memory.skills import promote_skill, skill_definition


kwargs = {
    "name": "Required field validation",
    "when_to_use": "A request may omit a required field before processing begins.",
    "inputs": ["request payload", "required field name"],
    "steps": [
        "Check the required field before accessing it.",
        "Raise the expected validation error when it is absent.",
    ],
    "verification": ["Run the focused request validation test."],
    "agent_id": "skill-test",
}

try:
    promote_skill(**kwargs, supporting_experience_ids=["experience-1"])
except ValueError as error:
    assert "two QA-approved" in str(error)
else:
    raise AssertionError("One experience without approval must not create a skill")

try:
    promote_skill(**kwargs, supporting_experience_ids=["experience-1", "experience-bad"])
except ValueError as error:
    assert "missing QA-approved" in str(error)
else:
    raise AssertionError("Rejected experience must not support a skill")

promoted = promote_skill(
    **kwargs,
    supporting_experience_ids=["experience-1", "experience-2"],
    supporting_principle_ids=["principle-1"],
)
assert promoted["promoted"]
assert promoted["supporting_experience_count"] == 2
assert promoted["skill"]["version"] == 1
assert promoted["skill"]["supporting_principle_ids"] == ["principle-1"]
assert stored[0]["type"] == "skill"
assert links == [
    ("experience-1", "skill-1", "supports", "skill-test"),
    ("experience-2", "skill-1", "supports", "skill-test"),
    ("principle-1", "skill-1", "supports", "skill-test"),
]
assert skill_definition(stored[0])["name"] == "Required field validation"
assert skill_definition({"skill_definition": "{not JSON"}) is None
assert skill_definition({"skill_definition": json.dumps({
    "schema_version": 1,
    "name": "Bad Skill",
    "when_to_use": "Too short",
})}) is None

manual = promote_skill(
    **kwargs,
    supporting_experience_ids=["experience-1"],
    human_approved=True,
)
assert manual["supporting_experience_count"] == 1

print("PASS: QA-backed skill promotion")
