"""Small deterministic cognition contracts for host certification."""


CONTRACT_SCHEMA_VERSION = 1
VALID_ASSERTIONS = {
    "requires_verification",
    "abstains_without_evidence",
    "excludes_nontrusted",
    "fail_open",
}


def _validate(contract):
    if not isinstance(contract, dict) or not str(contract.get("name", "")).strip():
        raise ValueError("contract needs a non-empty name.")
    assertions = contract.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        raise ValueError("contract.assertions must contain at least one assertion.")
    normalized = []
    for assertion in assertions:
        if not isinstance(assertion, dict) or assertion.get("rule") not in VALID_ASSERTIONS:
            raise ValueError("Each assertion must use a supported cognition rule.")
        normalized.append({
            "name": str(assertion.get("name") or assertion["rule"]),
            "rule": assertion["rule"],
        })
    return {"schema_version": CONTRACT_SCHEMA_VERSION, "name": str(contract["name"]).strip(), "assertions": normalized}


def evaluate_contract(contract, observations):
    """Evaluate host-supplied observations without invoking a provider."""
    contract = _validate(contract)
    if not isinstance(observations, dict):
        raise ValueError("observations must be an object.")
    records = observations.get("records", [])
    if not isinstance(records, list):
        raise ValueError("observations.records must be a list when provided.")
    results = []
    for assertion in contract["assertions"]:
        rule = assertion["rule"]
        if rule == "requires_verification":
            passed = observations.get("verification_required") is True
        elif rule == "abstains_without_evidence":
            passed = observations.get("evidence_available") is not True and observations.get("strategy") in {"normal_reasoning", "abstain"}
        elif rule == "excludes_nontrusted":
            passed = all(record.get("record_state", "trusted") == "trusted" for record in records if isinstance(record, dict))
        else:
            passed = observations.get("fail_open") is True
        results.append({"name": assertion["name"], "rule": rule, "passed": passed})
    return {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "name": contract["name"],
        "passed": all(item["passed"] for item in results),
        "results": results,
    }


def certify_host(host, events):
    """Certify the minimum lifecycle, QA, and privacy receipt contract."""
    if not isinstance(host, str) or not host.strip():
        raise ValueError("host must be a non-empty string.")
    if not isinstance(events, list) or not events:
        raise ValueError("events must contain host receipts.")
    names = {event.get("event") for event in events if isinstance(event, dict)}
    checks = [
        {"name": "lifecycle_started", "passed": "task_started" in names},
        {"name": "verification_boundary", "passed": "verification_finished" in names},
        {"name": "qa_gated_learning", "passed": all(
            event.get("event") != "verification_finished"
            or (event.get("capture") or {}).get("qa", {}).get("approved") is True
            for event in events if isinstance(event, dict)
        )},
        {"name": "fail_open_receipts", "passed": all(
            event.get("fail_open", False) is False for event in events if isinstance(event, dict)
        )},
        {"name": "privacy_boundary", "passed": all(
            event.get("privacy_safe", True) is True and not event.get("memory_contents")
            for event in events if isinstance(event, dict)
        )},
    ]
    return {
        "host": host,
        "certified": all(check["passed"] for check in checks),
        "checks": checks,
    }
