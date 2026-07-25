"""Accepted reflections must remain linked to their QA-approved experience."""

import importlib
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

capture = types.ModuleType("memory.capture")
capture.capture_memory = lambda **kwargs: {"hash": "experience-1"}
sys.modules["memory.capture"] = capture

principles = types.ModuleType("memory.principle_capture")
principles.capture_principles = lambda values, owner: []
sys.modules["memory.principle_capture"] = principles

captures = []
reflection = types.ModuleType("memory.reflection_capture")


def capture_reflection(value, **kwargs):
    captures.append({"value": value, **kwargs})
    return {"hash": "reflection-1"}


reflection.capture_reflection = capture_reflection
sys.modules["memory.reflection_capture"] = reflection

sys.modules.pop("memory.record_outcome", None)
record_outcome = importlib.import_module("memory.record_outcome").record_outcome

result = record_outcome(
    task="Validate a required request field",
    files=["validation.py"],
    summary="A missing field reached request processing before validation.",
    solution="Check the field before processing the request.",
    reflection="I reproduced the missing-field case before changing validation.",
    agent_id="reflection-test",
    qa_report={"verdict": "approved", "schema_version": 1, "evidence_summary": {}},
)

assert result["reflections"] == [{
    "text": "I reproduced the missing-field case before changing validation.",
    "id": "reflection-1",
    "source_experience_id": "experience-1",
}]
assert captures[0]["source_experience_id"] == "experience-1"
assert captures[0]["verification"]["qa_verdict"] == "approved"

print("PASS: reflection provenance")
