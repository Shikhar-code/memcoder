"""Plan outcomes are durable audits and never become retrieval guidance."""

import importlib
import os
import sys
import tempfile
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

sys.modules.pop("memory.plan_outcomes", None)
outcomes = importlib.import_module("memory.plan_outcomes")

audit_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl").name
os.unlink(audit_path)
os.environ["MEMCODER_AUDIT_PATH"] = audit_path

passed = outcomes.record_plan_outcome(
    plan_id="plan_1234567890abcdef1234",
    task="Validate a required request field.",
    qa_report={"verdict": "approved", "evidence_summary": {"passed_checks": 1}},
    agent_id="plan-test",
    applied_skill_id="skill-1",
)
assert passed["status"] == "succeeded"
assert passed["id"].startswith("audit_")

failed = outcomes.record_plan_outcome(
    plan_id="plan_1234567890abcdef1234",
    task="Validate a required request field.",
    qa_report={"verdict": "rejected", "evidence_summary": {"failed_checks": 1}},
    agent_id="plan-test",
)
assert failed["status"] == "failed"

unverified = outcomes.record_plan_outcome(
    plan_id="plan_1234567890abcdef1234",
    task="Validate a required request field.",
    qa_report={"verdict": "insufficient_evidence", "evidence_summary": {}},
    agent_id="plan-test",
)
assert unverified["status"] == "unverified"
history = outcomes.plan_outcome_history("plan_1234567890abcdef1234", agent_id="plan-test")
assert {entry["status"] for entry in history} == {"unverified", "failed", "succeeded"}
assert all(entry["id"].startswith("audit_") for entry in history)
assert all("plan_outcome" not in entry for entry in history)

try:
    outcomes.record_plan_outcome("wrong", "task", {"verdict": "approved"})
except ValueError as error:
    assert "plan_id" in str(error)
else:
    raise AssertionError("Non-MemCoder plan IDs must be rejected")

print("PASS: durable non-guidance plan outcomes")
