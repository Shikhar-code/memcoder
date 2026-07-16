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


def hierarchical_search(problem, agent_id, include_shared=True):
    search_calls.update(
        agent_id=agent_id,
        include_shared=include_shared
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

prepared = json.loads(
    server.memcoder_prepare(
        "A required field is missing.",
        agent_id="antigravity"
    )
)

assert prepared["strategy"] == "memory_guided"
assert prepared["experiences"][0]["task"] == (
    "Validate a required field"
)
assert "memcoder_record" in prepared["instructions"][-1]
assert search_calls == {
    "agent_id": "antigravity",
    "include_shared": True
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

recorded = json.loads(
    server.memcoder_record(
        task="Validate a required field",
        files=["api.py"],
        summary="A required field was missing.",
        solution="Validate it before processing.",
        agent_id="antigravity"
    )
)

assert recorded["experience_recorded"]
assert recorded["rejected"] == []
assert record_calls["agent_id"] == "antigravity"

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
