"""Deterministic reporting for matched MemCoder workflow evaluations."""

from collections import defaultdict
import math


VALID_CONDITIONS = {"baseline", "memory_guided", "skill_planned", "dreaming"}


def _number(value, field, minimum=0):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < minimum:
        raise ValueError(f"Run field '{field}' must be a number greater than or equal to {minimum}.")
    return value


def _run(run):
    if not isinstance(run, dict):
        raise ValueError("Each evaluation run must be an object.")
    task_id = run.get("task_id")
    condition = run.get("condition")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("Run field 'task_id' must be a non-empty string.")
    if condition not in VALID_CONDITIONS:
        raise ValueError("Run field 'condition' must be baseline, memory_guided, skill_planned, or dreaming.")
    if not isinstance(run.get("passed"), bool):
        raise ValueError("Run field 'passed' must be boolean.")
    normalized = {
        "task_id": task_id.strip(),
        "condition": condition,
        "passed": run["passed"],
    }
    for field in (
            "rework_count", "guidance_tokens", "latency_ms", "host_tokens",
            "estimated_tokens_avoided"):
        if field in run:
            normalized[field] = _number(run[field], field)
    for field in (
            "retrieval_relevant", "abstained", "abstention_correct", "harmful",
            "host_blocked", "guidance_used", "changed_action"):
        if field in run:
            if not isinstance(run[field], bool):
                raise ValueError(f"Run field '{field}' must be boolean when provided.")
            normalized[field] = run[field]
    return normalized


def _condition_summary(runs):
    total = len(runs)
    passed = sum(run["passed"] for run in runs)
    result = {
        "runs": total,
        "passed": passed,
        "pass_rate": round(passed / total, 2) if total else None,
    }
    for field, label in (("rework_count", "average_rework_count"), ("guidance_tokens", "average_guidance_tokens")):
        values = [run[field] for run in runs if field in run]
        result[label] = round(sum(values) / len(values), 2) if values else None
    relevant = [run["retrieval_relevant"] for run in runs if "retrieval_relevant" in run]
    result["retrieval_precision"] = round(sum(relevant) / len(relevant), 2) if relevant else None
    return result


def _rate(values):
    return round(sum(values) / len(values), 3) if values else None


def _percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)], 2)


def _release_readiness(by_task, runs):
    assisted = [run for run in runs if run["condition"] != "baseline"]
    paired = sum(
        "baseline" in conditions and any(
            condition in conditions for condition in ("memory_guided", "skill_planned", "dreaming")
        )
        for conditions in by_task.values()
    )
    relevance = [run["retrieval_relevant"] for run in assisted if "retrieval_relevant" in run]
    abstention = [run["abstention_correct"] for run in assisted if "abstention_correct" in run]
    harmful = [run["harmful"] for run in assisted if "harmful" in run]
    blocked = [run["host_blocked"] for run in assisted if "host_blocked" in run]
    latency = [run["latency_ms"] for run in assisted if "latency_ms" in run]
    dividends = [
        run["estimated_tokens_avoided"] - run.get("guidance_tokens", 0)
        for run in assisted if "estimated_tokens_avoided" in run
    ]
    changed = [
        run["changed_action"] for run in assisted
        if run.get("guidance_used") is True and "changed_action" in run
    ]
    metrics = {
        "paired_tasks": paired,
        "retrieval_precision": _rate(relevance),
        "correct_abstention": _rate(abstention),
        "harmful_transfer_rate": _rate(harmful),
        "host_blocking_failures": sum(blocked) if blocked else None,
        "intervention_action_change_rate": _rate(changed),
        "p95_latency_ms": _percentile(latency, 0.95),
        "median_token_dividend": _percentile(dividends, 0.50),
    }
    definitions = (
        ("paired_tasks", ">=", 24),
        ("retrieval_precision", ">=", 0.75),
        ("correct_abstention", ">=", 0.85),
        ("harmful_transfer_rate", "<=", 0.03),
        ("host_blocking_failures", "==", 0),
        ("intervention_action_change_rate", ">=", 0.40),
        ("p95_latency_ms", "<=", 1000),
        ("median_token_dividend", ">", 0),
    )
    gates = []
    for name, operator, target in definitions:
        value = metrics[name]
        passed = value is not None and {
            ">=": lambda: value >= target,
            "<=": lambda: value <= target,
            "==": lambda: value == target,
            ">": lambda: value > target,
        }[operator]()
        gates.append({"name": name, "value": value, "operator": operator, "target": target, "passed": passed})
    return {"ready": all(gate["passed"] for gate in gates), "metrics": metrics, "gates": gates}


def evaluate_runs(runs):
    """Summarize explicit run evidence; never infer missing host measurements."""
    if not isinstance(runs, list) or not runs:
        raise ValueError("Evaluation input must include at least one run.")
    normalized = [_run(run) for run in runs]
    by_condition = defaultdict(list)
    by_task = defaultdict(dict)
    for run in normalized:
        by_condition[run["condition"]].append(run)
        if run["condition"] in by_task[run["task_id"]]:
            raise ValueError("Each task_id may have only one run per condition.")
        by_task[run["task_id"]][run["condition"]] = run

    matched = [
        task_id for task_id, conditions in by_task.items()
        if "baseline" in conditions and "skill_planned" in conditions
    ]
    dream_matched = [
        task_id for task_id, conditions in by_task.items()
        if "baseline" in conditions and "dreaming" in conditions
    ]
    paired_changes = []
    for task_id in matched:
        baseline = by_task[task_id]["baseline"]
        planned = by_task[task_id]["skill_planned"]
        paired_changes.append({
            "task_id": task_id,
            "baseline_passed": baseline["passed"],
            "skill_planned_passed": planned["passed"],
            "pass_changed": int(planned["passed"]) - int(baseline["passed"]),
        })
    paired_dream_changes = []
    for task_id in dream_matched:
        baseline = by_task[task_id]["baseline"]
        dreaming = by_task[task_id]["dreaming"]
        paired_dream_changes.append({
            "task_id": task_id,
            "baseline_passed": baseline["passed"],
            "dreaming_passed": dreaming["passed"],
            "pass_changed": int(dreaming["passed"]) - int(baseline["passed"]),
        })

    return {
        "schema_version": 1,
        "conditions": {
            condition: _condition_summary(by_condition.get(condition, []))
            for condition in ("baseline", "memory_guided", "skill_planned")
        },
        "matched_baseline_skill_planned_tasks": len(matched),
        "paired_pass_changes": paired_changes,
        "matched_baseline_dreaming_tasks": len(dream_matched),
        "paired_dream_pass_changes": paired_dream_changes,
        "release_readiness": _release_readiness(by_task, normalized),
        "limitations": [
            "Results describe only host-supplied runs and measurements.",
            "A pass-rate difference is not causal proof without matched tasks and sufficient sample size.",
            "MemCoder does not judge task correctness; hosts must supply pass/fail evidence.",
        ],
    }
