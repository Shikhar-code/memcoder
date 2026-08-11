"""Cognition contracts and host certification remain deterministic."""

from memory.contracts import certify_host, evaluate_contract


contract = {
    "name": "safe-retrieval",
    "assertions": [
        {"rule": "requires_verification"},
        {"rule": "abstains_without_evidence"},
        {"rule": "excludes_nontrusted"},
        {"rule": "fail_open"},
    ],
}
result = evaluate_contract(contract, {
    "verification_required": True,
    "evidence_available": False,
    "strategy": "normal_reasoning",
    "records": [{"record_state": "trusted"}],
    "fail_open": True,
})
assert result["passed"] is True

certified = certify_host("test-host", [
    {"event": "task_started", "fail_open": False},
    {
        "event": "verification_finished", "fail_open": False,
        "capture": {"qa": {"approved": True}},
    },
])
assert certified["certified"] is True
assert any(check["name"] == "privacy_boundary" for check in certified["checks"])

untrusted = certify_host("test-host", [
    {"event": "task_started", "fail_open": False, "memory_contents": "raw transcript"},
    {"event": "verification_finished", "fail_open": False, "capture": {"qa": {"approved": True}}},
])
assert untrusted["certified"] is False

print("PASS: cognition contracts and host certification")
