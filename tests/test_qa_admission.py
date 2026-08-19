"""Beta 2 QA must block unsupported or failed learning outcomes."""

import importlib
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

from memory.qa import evaluate_outcome_qa


OUTCOME = {
    "task": "Reject a blank project name before processing the request.",
    "files": ["request_validation.py", "test_request_validation.py"],
    "summary": "A blank project name previously reached request processing.",
    "solution": "Validate the project name before reading or normalizing it.",
}

PASSING_EVIDENCE = {
    "checks": [{
        "name": "focused request validation test",
        "kind": "test",
        "status": "passed",
        "command": "python test_request_validation.py",
        "output": "PASS: request validation",
    }]
}


approved = evaluate_outcome_qa(**OUTCOME, evidence=PASSING_EVIDENCE)
assert approved["verdict"] == "approved"
assert approved["approved"]
assert approved["evidence_summary"]["passed_checks"] == ["focused request validation test"]
assert approved["verification_playbook"] == [{
    "name": "focused request validation test",
    "kind": "test",
    "command": "python test_request_validation.py",
}]

missing = evaluate_outcome_qa(**OUTCOME, evidence=None)
assert missing["verdict"] == "insufficient_evidence"
assert not missing["approved"]

failed = evaluate_outcome_qa(**OUTCOME, evidence={
    "checks": [{
        "name": "focused request validation test",
        "kind": "test",
        "status": "failed",
        "command": "python test_request_validation.py",
        "output": "FAIL: expected ValueError",
    }]
})
assert failed["verdict"] == "rejected"
assert not failed["approved"]

unsupported = evaluate_outcome_qa(**OUTCOME, evidence={
    "checks": [{
        "name": "claimed test",
        "kind": "test",
        "status": "passed",
        "command": "python test_request_validation.py",
    }]
})
assert unsupported["verdict"] == "insufficient_evidence"

normalized = evaluate_outcome_qa(**OUTCOME, evidence={
    "checks": [{
        "name": "installed package diagnostic",
        "kind": "assertion",
        "passed": True,
        "command": "python -c print_version",
        "output": "0.3.1b1",
    }]
})
assert normalized["verdict"] == "approved"
assert normalized["evidence_summary"]["check_kinds"] == ["diagnostic"]


captures = []
capture = types.ModuleType("memory.capture")


def capture_memory(**kwargs):
    captures.append(kwargs)
    return {"hash": "experience-test"}


capture.capture_memory = capture_memory
sys.modules["memory.capture"] = capture

principle = types.ModuleType("memory.principle_capture")
principle.capture_principles = lambda values, owner: None
sys.modules["memory.principle_capture"] = principle

reflection = types.ModuleType("memory.reflection_capture")
reflection.capture_reflection = lambda value, **kwargs: {"hash": "reflection-test"}
sys.modules["memory.reflection_capture"] = reflection

sys.modules.pop("memory.record_outcome", None)
record_outcome = importlib.import_module("memory.record_outcome").record_outcome

blocked = record_outcome(**OUTCOME, agent_id="qa-test", qa_report=missing)
assert blocked["experience"] is None
assert not captures

stored = record_outcome(**OUTCOME, agent_id="qa-test", qa_report=approved)
assert stored["experience"] is not None
assert stored["experience"]["id"] == "experience-test"
assert len(captures) == 1
assert '"qa_verdict": "approved"' in captures[0]["verification"]

print("PASS: QA evidence admission")
