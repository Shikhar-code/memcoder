"""Plan outcomes are durable audits and never become retrieval guidance."""

import importlib
import json
import sys
import types
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

captures = []
capture = types.ModuleType("memory.capture")


def capture_memory(**kwargs):
    captures.append(kwargs)
    return {"hash": f"plan-outcome-{len(captures)}"}


capture.capture_memory = capture_memory
sys.modules["memory.capture"] = capture
sys.modules.pop("memory.plan_outcomes", None)
outcomes = importlib.import_module("memory.plan_outcomes")

passed = outcomes.record_plan_outcome(
    plan_id="plan_1234567890abcdef1234",
    task="Validate a required request field.",
    qa_report={"verdict": "approved", "evidence_summary": {"passed_checks": 1}},
    agent_id="plan-test",
    applied_skill_id="skill-1",
)
assert passed["status"] == "succeeded"
assert captures[0]["memory_type"] == "plan_outcome"
assert captures[0]["metadata"]["plan_status"] == "succeeded"
assert json.loads(captures[0]["verification"])["qa_verdict"] == "approved"

failed = outcomes.record_plan_outcome(
    plan_id="plan_1234567890abcdef1234",
    task="Validate a required request field.",
    qa_report={"verdict": "rejected", "evidence_summary": {"failed_checks": 1}},
    agent_id="plan-test",
)
assert failed["status"] == "failed"
assert captures[1]["metadata"]["plan_status"] == "failed"

unverified = outcomes.record_plan_outcome(
    plan_id="plan_1234567890abcdef1234",
    task="Validate a required request field.",
    qa_report={"verdict": "insufficient_evidence", "evidence_summary": {}},
    agent_id="plan-test",
)
assert unverified["status"] == "unverified"

history_calls = {}


class FakeCollection:
    def get(self, where, include):
        history_calls.update(where=where, include=include)
        return {
            "ids": ["plan-outcome-old", "plan-outcome-new"],
            "metadatas": [
                {
                    "plan_id": "plan_1234567890abcdef1234",
                    "plan_status": "failed",
                    "applied_skill_id": "skill-1",
                    "timestamp": "2026-01-01T00:00:00",
                    "verification": json.dumps({"qa_verdict": "rejected"}),
                },
                {
                    "plan_id": "plan_1234567890abcdef1234",
                    "plan_status": "succeeded",
                    "applied_skill_id": "skill-1",
                    "timestamp": "2026-01-02T00:00:00",
                    "verification": json.dumps({"qa_verdict": "approved"}),
                },
            ],
        }


chroma = types.ModuleType("memory.chroma_client")
chroma.collection = FakeCollection()
sys.modules["memory.chroma_client"] = chroma
history = outcomes.plan_outcome_history("plan_1234567890abcdef1234", agent_id="plan-test")
assert [entry["status"] for entry in history] == ["succeeded", "failed"]
assert history_calls["include"] == ["metadatas"]

try:
    outcomes.record_plan_outcome("wrong", "task", {"verdict": "approved"})
except ValueError as error:
    assert "plan_id" in str(error)
else:
    raise AssertionError("Non-MemCoder plan IDs must be rejected")

print("PASS: durable non-guidance plan outcomes")
