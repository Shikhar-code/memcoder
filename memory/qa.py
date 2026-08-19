"""Deterministic QA admission for outcomes proposed by an agent host.

MemCoder evaluates structured evidence supplied by the host.  It never runs
host commands, interprets arbitrary source code, or requires a provider model.
"""

from memory.quality import (
    is_meaningful_text,
    is_valid_experience,
    is_valid_principle,
    is_valid_reflection,
)


QA_SCHEMA_VERSION = 1
CHECK_KINDS = {"test", "build", "lint", "assertion", "diagnostic", "manual_review"}
CHECK_STATUSES = {"passed", "failed", "skipped"}


def _gate(name, status, reason):
    return {"name": name, "status": status, "reason": reason}


def _text(value, minimum_words=1):
    return is_meaningful_text(value, minimum_words=minimum_words)


def _check_has_proof(check):
    """Return whether one passed check contains inspectable host evidence."""
    kind = check.get("kind")
    if kind in {"test", "build", "lint", "diagnostic"}:
        return _text(check.get("command"), 1) and _text(check.get("output"), 1)
    if kind == "assertion":
        return _text(check.get("assertion"), 2) and _text(check.get("actual"), 1)
    if kind == "manual_review":
        return _text(check.get("reviewer"), 1) and _text(check.get("notes"), 2)
    return False


def _normalize_check(check):
    """Accept common host evidence shapes without weakening proof requirements."""
    if not isinstance(check, dict):
        return check
    normalized = dict(check)
    aliases = {"review": "manual_review", "manual": "manual_review"}
    normalized["kind"] = aliases.get(normalized.get("kind"), normalized.get("kind"))
    if normalized.get("status") is None and isinstance(normalized.get("passed"), bool):
        normalized["status"] = "passed" if normalized["passed"] else "failed"
    if (
            normalized.get("kind") == "assertion"
            and not normalized.get("assertion")
            and normalized.get("command")
            and normalized.get("output")):
        normalized["kind"] = "diagnostic"
    return normalized


def evaluate_outcome_qa(
        task,
        files,
        summary,
        solution,
        evidence,
        reflection=None,
        principles=None):
    """Return an auditable admission verdict without storing anything.

    ``approved`` means the outcome has valid structure and at least one passed,
    inspectable verification check.  ``rejected`` means supplied evidence
    explicitly failed.  ``insufficient_evidence`` means the host did not
    provide enough evidence to make a safe learning decision.
    """
    gates = []
    experience = {
        "task": task,
        "files": files,
        "summary": summary,
        "solution": solution,
    }
    if is_valid_experience(experience):
        gates.append(_gate("outcome_structure", "passed", "Task, files, summary, and solution are meaningful."))
    else:
        gates.append(_gate("outcome_structure", "failed", "Task, files, summary, and solution must be meaningful."))

    field_rejections = []
    if reflection and not is_valid_reflection(reflection):
        field_rejections.append("reflection: not a concise investigation observation")
    invalid_principles = [
        principle for principle in (principles or []) if not is_valid_principle(principle)
    ]
    if invalid_principles:
        field_rejections.append(
            f"principles: {len(invalid_principles)} item(s) were not meaningful"
        )

    if not isinstance(evidence, dict):
        gates.append(_gate("verification_evidence", "missing", "Provide an evidence object with verification checks."))
        return _report("insufficient_evidence", gates, field_rejections, [])

    checks = evidence.get("checks")
    if not isinstance(checks, list) or not checks:
        gates.append(_gate("verification_evidence", "missing", "Provide at least one verification check."))
        return _report("insufficient_evidence", gates, field_rejections, [])

    normalized_checks = []
    malformed = False
    for index, raw_check in enumerate(checks):
        check = _normalize_check(raw_check)
        if not isinstance(check, dict):
            malformed = True
            field_rejections.append(f"evidence.checks[{index}]: expected an object")
            continue
        kind = check.get("kind")
        status = check.get("status")
        name = check.get("name")
        if kind not in CHECK_KINDS or status not in CHECK_STATUSES or not _text(name, 1):
            malformed = True
            field_rejections.append(
                f"evidence.checks[{index}]: use a named {sorted(CHECK_KINDS)} check "
                f"with status passed, failed, or skipped"
            )
            continue
        normalized_checks.append(check)

    if malformed:
        gates.append(_gate(
            "verification_schema",
            "failed",
            "Fix the indexed evidence.checks entries listed in field_rejections.",
        ))
    else:
        gates.append(_gate("verification_schema", "passed", "Verification checks use the supported schema."))

    failed = [check for check in normalized_checks if check["status"] == "failed"]
    passed = [check for check in normalized_checks if check["status"] == "passed"]
    unsupported = [check for check in passed if not _check_has_proof(check)]

    if failed:
        gates.append(_gate("verification_result", "failed", "At least one supplied verification check failed."))
    elif not passed:
        gates.append(_gate("verification_result", "missing", "No verification check passed."))
    elif unsupported:
        gates.append(_gate(
            "verification_proof",
            "missing",
            "Passed tests/builds/lints/diagnostics need command+output; assertions need "
            "assertion+actual; manual reviews need reviewer+notes.",
        ))
    else:
        gates.append(_gate("verification_result", "passed", "At least one verification check passed with inspectable evidence."))

    statuses = {gate["status"] for gate in gates}
    if "failed" in statuses:
        verdict = "rejected"
    elif "missing" in statuses:
        verdict = "insufficient_evidence"
    else:
        verdict = "approved"
    return _report(verdict, gates, field_rejections, normalized_checks)


def _report(verdict, gates, field_rejections, checks):
    playbook = []
    for check in checks:
        if check.get("status") != "passed":
            continue
        item = {"name": check["name"], "kind": check["kind"]}
        if check["kind"] in {"test", "build", "lint", "diagnostic"}:
            item["command"] = check.get("command", "")
        elif check["kind"] == "assertion":
            item["assertion"] = check.get("assertion", "")
        else:
            item["reviewer"] = check.get("reviewer", "")
        playbook.append(item)
    return {
        "schema_version": QA_SCHEMA_VERSION,
        "verdict": verdict,
        "approved": verdict == "approved",
        "gates": gates,
        "field_rejections": field_rejections,
        "evidence_summary": {
            "check_count": len(checks),
            "passed_checks": [check["name"] for check in checks if check["status"] == "passed"],
            "failed_checks": [check["name"] for check in checks if check["status"] == "failed"],
            "check_kinds": sorted({check["kind"] for check in checks}),
        },
        "verification_playbook": playbook,
    }
