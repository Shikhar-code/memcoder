import importlib
import json
import sys
import types
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)


class FakeMCP:
    def __init__(self, name):
        self.name = name

    def tool(self):
        return lambda function: function


fastmcp = types.ModuleType("fastmcp")
fastmcp.FastMCP = FakeMCP
sys.modules["fastmcp"] = fastmcp

search = types.ModuleType("memory.hierarchical_search")
search_calls = {}


def hierarchical_search(problem, agent_id, include_shared=True, include_skills=True):
    search_calls.update(
        agent_id=agent_id,
        include_shared=include_shared,
        include_skills=include_skills,
    )
    return {
    "confidence": 0.73,
    "strategy": "memory_guided",
    "experiences": [{
        "task": "Validate a required field",
        "summary": "A required field was missing.",
        "solution": "Validate it before processing.",
        "files": ["api.py"],
        "score": 0.542,
        "retrieval_confidence": 0.73
    }],
    "mistakes": [],
    "principles": [],
    "reflections": []
    }


search.hierarchical_search = hierarchical_search
sys.modules["memory.hierarchical_search"] = search

record_calls = {}
record = types.ModuleType("memory.record_outcome")


def record_outcome(**kwargs):
    record_calls.update(kwargs)
    return {
        "experience": {"task": kwargs["task"]},
        "reflections": [],
        "principles": [],
        "rejected": []
    }


record.record_outcome = record_outcome
sys.modules["memory.record_outcome"] = record

markdown_calls = {}
markdown_import = types.ModuleType("memory.markdown_import")


def import_markdown(**kwargs):
    markdown_calls.update(kwargs)
    return {
        "source_name": kwargs["source_name"],
        "candidates": [{"task": "Validate input"}],
        "rejected": [],
        "approved": kwargs["approve"],
        "recorded": []
    }


markdown_import.import_markdown = import_markdown


def import_markdown_file(**kwargs):
    markdown_calls.clear()
    markdown_calls.update(kwargs)
    return {
        "source_name": kwargs["file_path"],
        "candidates": [{"task": "Validate input"}],
        "rejected": [],
        "approved": kwargs["approve"],
        "recorded": []
    }


markdown_import.import_markdown_file = import_markdown_file
sys.modules["memory.markdown_import"] = markdown_import

sys.modules.pop("adapters.mcp.server", None)
server = importlib.import_module("adapters.mcp.server")

intervene_calls = {}
server.intervene_cognition = lambda **kwargs: intervene_calls.update(kwargs) or {
    "intervention": {"mode": "none"}, "budget": {"within_budget": True}
}
intervention = json.loads(server.memcoder_intervene(
    "Investigate a required field failure.",
    agent_id="codex",
    include_shared=False,
    token_budget=300,
))
assert intervention["intervention"]["mode"] == "none"
assert intervene_calls == {
    "problem": "Investigate a required field failure.",
    "agent_id": "codex",
    "include_shared": False,
    "environment": None,
    "token_budget": 300,
}

checkpoint_calls = {}
server.checkpoint_cognition = lambda **kwargs: checkpoint_calls.update(kwargs) or {
    "id": "checkpoint-1"
}
checkpoint = json.loads(server.memcoder_checkpoint(
    "task-1", {"facts": ["The test fails."]}, agent_id="codex"
))
assert checkpoint["id"] == "checkpoint-1"
assert checkpoint_calls["task_id"] == "task-1"
assert checkpoint_calls["update"]["facts"] == ["The test fails."]

state_calls = {}
server.task_state_cognition = lambda **kwargs: state_calls.update(kwargs) or {
    "checkpoint": None
}
state = json.loads(server.memcoder_task_state("task-1", agent_id="codex"))
assert state["checkpoint"] is None
assert state_calls == {"task_id": "task-1", "agent_id": "codex"}

start_calls = {}
server.start_cognition = lambda **kwargs: start_calls.update(kwargs) or {
    "brief": {}, "plan": {"mode": "foundation", "steps": []}
}
started = json.loads(
    server.memcoder_start(
        "A required field is missing.",
        agent_id="antigravity",
        include_shared=False,
    )
)
assert started["plan"]["mode"] == "foundation"
assert start_calls == {
    "problem": "A required field is missing.",
    "agent_id": "antigravity",
    "include_shared": False,
}

prepared = json.loads(
    server.memcoder_prepare(
        "A required field is missing.",
        agent_id="antigravity"
    )
)

assert prepared["strategy"] == "memory_guided"
assert prepared["detail_level"] == "brief"
assert prepared["brief"]["evidence"][0]["task"] == (
    "Validate a required field"
)
assert "QA approves" in prepared["instructions"][-1]
assert search_calls == {
    "agent_id": "antigravity",
    "include_shared": True,
    "include_skills": True,
}

isolated = json.loads(
    server.memcoder_prepare(
        "A required field is missing.",
        agent_id="antigravity",
        include_shared=False
    )
)

assert isolated["include_shared"] is False
assert search_calls["include_shared"] is False

without_skills = json.loads(
    server.memcoder_prepare(
        "A required field is missing.",
        agent_id="antigravity",
        include_skills=False,
    )
)
assert without_skills["include_skills"] is False
assert search_calls["include_skills"] is False

expanded = json.loads(
    server.memcoder_prepare(
        "A required field is missing.",
        agent_id="antigravity",
        detail_level="full"
    )
)
assert expanded["experiences"][0]["task"] == "Validate a required field"

plan_calls = {}
server.plan_cognition = lambda **kwargs: plan_calls.update(kwargs) or {
    "plan": {"mode": "foundation", "steps": []}
}
planned = json.loads(
    server.memcoder_plan(
        "A required field is missing.",
        agent_id="antigravity",
        include_shared=False,
    )
)
assert planned["plan"]["mode"] == "foundation"
assert plan_calls == {
    "problem": "A required field is missing.",
    "agent_id": "antigravity",
    "include_shared": False,
}

history_calls = {}
server.plan_history_cognition = lambda **kwargs: history_calls.update(kwargs) or {
    "plan_id": kwargs["plan_id"], "outcomes": []
}
history = json.loads(
    server.memcoder_plan_history(
        "plan_1234567890abcdef1234",
        agent_id="antigravity",
    )
)
assert history["outcomes"] == []
assert history_calls == {
    "plan_id": "plan_1234567890abcdef1234",
    "agent_id": "antigravity",
}

health_calls = {}
server.skill_health_cognition = lambda **kwargs: health_calls.update(kwargs) or {
    "skill_id": kwargs["skill_id"], "status": "unproven"
}
health = json.loads(server.memcoder_skill_health("skill-1", agent_id="antigravity"))
assert health["status"] == "unproven"
assert health_calls == {"skill_id": "skill-1", "agent_id": "antigravity"}

evaluation_calls = {}
server.evaluate_cognition = lambda runs: evaluation_calls.update(runs=runs) or {
    "conditions": {"baseline": {"runs": len(runs)}}
}
evaluation = json.loads(server.memcoder_evaluate([
    {"task_id": "task-1", "condition": "baseline", "passed": True}
]))
assert evaluation["conditions"]["baseline"]["runs"] == 1
assert evaluation_calls["runs"][0]["task_id"] == "task-1"

recorded = json.loads(
    server.memcoder_record(
        task="Validate a required field",
        files=["api.py"],
        summary="A required field was missing.",
        solution="Validate it before processing.",
        evidence={
            "checks": [{
                "name": "focused validation test",
                "kind": "test",
                "status": "passed",
                "command": "python test_validation.py",
                "output": "PASS"
            }]
        },
        agent_id="antigravity"
    )
)

assert recorded["experience_recorded"]
assert recorded["rejected"] == []
assert record_calls["agent_id"] == "antigravity"

skill_calls = {}
server.promote_skill_cognition = lambda **kwargs: skill_calls.update(kwargs) or {
    "promoted": True,
    "id": "skill-1",
}
promoted = json.loads(
    server.memcoder_promote_skill(
        name="Required field validation",
        when_to_use="A required request field may be missing before processing.",
        inputs=["request payload"],
        steps=["Check the field.", "Run the focused test."],
        verification=["Focused test passes."],
        supporting_experience_ids=["experience-1", "experience-2"],
        agent_id="antigravity",
    )
)
assert promoted["promoted"]
assert skill_calls["supporting_experience_ids"] == ["experience-1", "experience-2"]
assert skill_calls["supporting_principle_ids"] is None

imported = json.loads(
    server.memcoder_import_markdown(
        markdown="- Validate input",
        source_name="AGENTS.md",
        agent_id="antigravity",
        approve=False
    )
)

assert imported["candidates"][0]["task"] == "Validate input"
assert markdown_calls == {
    "markdown": "- Validate input",
    "source_name": "AGENTS.md",
    "agent_id": "antigravity",
    "approve": False
}

file_imported = json.loads(
    server.memcoder_import_markdown_file(
        file_path="AGENTS.md",
        agent_id="antigravity",
        approve=False
    )
)

assert file_imported["candidates"][0]["task"] == "Validate input"
assert markdown_calls == {
    "file_path": "AGENTS.md",
    "agent_id": "antigravity",
    "approve": False
}

print("PASS: provider-free MCP cognition")
