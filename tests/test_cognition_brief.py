"""Beta 2 compact preparation must be bounded and expand only on request."""

import importlib
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

search = types.ModuleType("memory.hierarchical_search")


def hierarchical_search(problem, agent_id, include_shared=True, include_skills=True):
    return {
        "confidence": 0.82,
        "strategy": "memory_guided",
        "experiences": [{
            "id": "experience-1",
            "task": "Validate required project fields before processing.",
            "summary": "A missing project field reached string processing.",
            "solution": "Check required fields before calling string operations.",
            "files": ["project_validation.py"],
            "retrieval_confidence": 0.82,
        }],
        "mistakes": [{
            "id": "mistake-1",
            "task": "Assumed validation ran before accessing the request.",
            "summary": "Validation order was not checked.",
            "solution": "Inspect validation order first.",
            "files": ["project_validation.py"],
            "retrieval_confidence": 0.79,
        }],
        "principles": [{
            "id": "principle-1",
            "task": "Validate required values before processing input.",
            "summary": "Validate required values before processing input.",
            "solution": "Principle",
            "files": ["principle"],
            "retrieval_confidence": 0.76,
        }],
        "reflections": [],
        "skills": [{
            "id": "skill-1",
            "task": "Required field validation",
            "summary": "Use the validated required-field procedure.",
            "solution": "Check before string operations.",
            "files": ["skill"],
            "retrieval_confidence": 0.81,
            "health": {
                "status": "trusted",
                "attempts": 100,
                "succeeded": 90,
                "failed": 10,
                "unverified": 0,
                "success_rate": 0.9,
                "automatic_retrieval_allowed": True,
            },
        }],
    }


search.hierarchical_search = hierarchical_search
sys.modules["memory.hierarchical_search"] = search
sys.modules.pop("api.cognition", None)
cognition = importlib.import_module("api.cognition")

brief = cognition.prepare_cognition(
    "A project name is missing from an incoming request.",
    agent_id="brief-test",
    include_shared=False,
)
assert brief["detail_level"] == "brief"
assert brief["include_skills"] is True
assert "experiences" not in brief
assert len(brief["brief"]["evidence"]) == 4
assert brief["brief"]["budget"]["within_budget"]
assert brief["brief"]["evidence"][0]["health"] == "trusted"
assert brief["available_detail"]["experiences"] == 1

full = cognition.prepare_cognition(
    "A project name is missing from an incoming request.",
    agent_id="brief-test",
    detail_level="full",
)
assert full["experiences"][0]["id"] == "experience-1"

without_skills = cognition.prepare_cognition(
    "A project name is missing from an incoming request.",
    agent_id="brief-test",
    include_skills=False,
)
assert without_skills["include_skills"] is False

try:
    cognition.prepare_cognition("task", detail_level="everything")
except ValueError as error:
    assert "detail_level" in str(error)
else:
    raise AssertionError("Invalid detail level should be rejected")

print("PASS: compact cognition brief")
