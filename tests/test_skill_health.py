"""Repeated failed plan outcomes must remove a Skill from automatic reuse."""

import json
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))


audit_store = types.ModuleType("memory.audit_store")


def outcomes_for_skill(skill_id, agent_id):
    statuses = {
        "skill-failing": ["failed", "failed"],
        "skill-trusted": ["succeeded", "succeeded", "succeeded", "failed"],
        "skill-monitor": ["succeeded", "failed"],
        "skill-new": [],
    }[skill_id]
    return [{"status": status, "owner": agent_id} for status in statuses]


audit_store.outcomes_for_skill = outcomes_for_skill
sys.modules["memory.audit_store"] = audit_store

from memory.skill_health import eligible_skills, skill_health

failing = skill_health("skill-failing", agent_id="health-test")
assert failing["status"] == "review_required"
assert not failing["automatic_retrieval_allowed"]

trusted = skill_health("skill-trusted", agent_id="health-test")
assert trusted["status"] == "trusted"
assert trusted["success_rate"] == 0.75

monitor = skill_health("skill-monitor", agent_id="health-test")
assert monitor["status"] == "monitor"

new = skill_health("skill-new", agent_id="health-test")
assert new["status"] == "unproven"
assert new["automatic_retrieval_allowed"]

skills = eligible_skills(
    [{"id": "skill-failing"}, {"id": "skill-trusted"}, {"id": "skill-new"}],
    agent_id="health-test",
)
assert [skill["id"] for skill in skills] == ["skill-trusted", "skill-new"]
assert skills[0]["health"]["status"] == "trusted"

# Verify the production retrieval boundary actually withholds review-required
# Skills before a brief or plan can see them.
embedder = types.ModuleType("memory.embedder")
embedder.embed = lambda problem: [0.0, 1.0]
sys.modules["memory.embedder"] = embedder

search = types.ModuleType("memory.search")
skill_definition = json.dumps({
    "schema_version": 1,
    "name": "Required field validation",
    "when_to_use": "A request may omit a required field before processing starts.",
    "inputs": ["request"],
    "steps": ["Check the field.", "Raise the expected error."],
    "verification": ["Run the focused test."],
    "supporting_experience_ids": ["experience-1"],
    "supporting_principle_ids": [],
    "human_approved": True,
    "version": 1,
})


def search_memory(query_embedding, k, memory_type, agent_id, include_shared):
    if memory_type != "skill":
        return []
    return [{
        "id": "skill-failing",
        "type": "skill",
        "task": "Required field validation",
        "summary": "Use a validation procedure.",
        "solution": "Check then raise.",
        "files": ["skill"],
        "score": 0.1,
        "skill_definition": skill_definition,
    }]


search.search_memory = search_memory
sys.modules["memory.search"] = search
sys.modules.pop("memory.hierarchical_search", None)
from memory.hierarchical_search import hierarchical_search

retrieved = hierarchical_search(
    "Validate the required request field.",
    agent_id="health-test",
    include_shared=False,
)
assert retrieved["skills"] == []

print("PASS: skill health feedback policy")
