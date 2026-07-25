"""Evaluation reporting must be explicit, matched, and non-causal by default."""

import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

from memory.evaluation import evaluate_runs


report = evaluate_runs([
    {"task_id": "task-1", "condition": "baseline", "passed": False, "rework_count": 2},
    {"task_id": "task-1", "condition": "memory_guided", "passed": True, "retrieval_relevant": True, "guidance_tokens": 120},
    {"task_id": "task-1", "condition": "skill_planned", "passed": True, "rework_count": 0, "retrieval_relevant": True, "guidance_tokens": 140},
    {"task_id": "task-2", "condition": "baseline", "passed": True},
    {"task_id": "task-2", "condition": "skill_planned", "passed": True},
])

assert report["conditions"]["baseline"]["pass_rate"] == 0.5
assert report["conditions"]["memory_guided"]["retrieval_precision"] == 1.0
assert report["conditions"]["skill_planned"]["average_rework_count"] == 0.0
assert report["matched_baseline_skill_planned_tasks"] == 2
assert report["paired_pass_changes"][0]["pass_changed"] == 1
assert "not causal proof" in report["limitations"][1]

try:
    evaluate_runs([
        {"task_id": "task-1", "condition": "baseline", "passed": True},
        {"task_id": "task-1", "condition": "baseline", "passed": True},
    ])
except ValueError as error:
    assert "only one run" in str(error)
else:
    raise AssertionError("Duplicate task-condition records must be rejected")

print("PASS: explicit evaluation reporting")
