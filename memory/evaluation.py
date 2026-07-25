"""Deterministic reporting for matched MemCoder workflow evaluations."""

from collections import defaultdict


VALID_CONDITIONS = {"baseline", "memory_guided", "skill_planned"}


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
        raise ValueError("Run field 'condition' must be baseline, memory_guided, or skill_planned.")
    if not isinstance(run.get("passed"), bool):
        raise ValueError("Run field 'passed' must be boolean.")
    normalized = {
        "task_id": task_id.strip(),
        "condition": condition,
        "passed": run["passed"],
    }
    for field in ("rework_count", "guidance_tokens"):
        if field in run:
            normalized[field] = _number(run[field], field)
    if "retrieval_relevant" in run:
        if not isinstance(run["retrieval_relevant"], bool):
            raise ValueError("Run field 'retrieval_relevant' must be boolean when provided.")
        normalized["retrieval_relevant"] = run["retrieval_relevant"]
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

    return {
        "schema_version": 1,
        "conditions": {
            condition: _condition_summary(by_condition.get(condition, []))
            for condition in ("baseline", "memory_guided", "skill_planned")
        },
        "matched_baseline_skill_planned_tasks": len(matched),
        "paired_pass_changes": paired_changes,
        "limitations": [
            "Results describe only host-supplied runs and measurements.",
            "A pass-rate difference is not causal proof without matched tasks and sufficient sample size.",
            "MemCoder does not judge task correctness; hosts must supply pass/fail evidence.",
        ],
    }
