"""Record admission must explain why an optional memory was rejected."""

import importlib
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

captures = []


capture = types.ModuleType("memory.capture")
capture.capture_memory = lambda **kwargs: captures.append(("experience", kwargs))
sys.modules["memory.capture"] = capture

principles = types.ModuleType("memory.principle_capture")
principles.capture_principles = lambda values, owner: captures.append(
    ("principles", values)
)
sys.modules["memory.principle_capture"] = principles

reflection = types.ModuleType("memory.reflection_capture")
reflection.capture_reflection = lambda value, owner: captures.append(
    ("reflection", value)
)
sys.modules["memory.reflection_capture"] = reflection

sys.modules.pop("memory.record_outcome", None)
record_outcome = importlib.import_module("memory.record_outcome").record_outcome

result = record_outcome(
    task="Validate a required value",
    files=["validator.py"],
    summary="A required value caused an unexpected KeyError.",
    solution="Validate the value before reading it.",
    reflection="I implemented explicit validation before calling strip.",
    principles=["Validate required input before processing it."],
    agent_id="test"
)

assert result["experience"] is not None
assert result["reflections"] == []
assert any(item.startswith("reflection:") for item in result["rejected"])
assert len(captures) == 2

print("PASS: record quality feedback")
