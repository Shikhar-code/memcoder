"""Beta 2.6 keeps failure learning and cognitive branches local, proven, and reversible."""

import json
import os
import tempfile
from pathlib import Path

from memory.cognitive_branch import (
    add_proof_obligation,
    cognitive_diff,
    complete_proof_obligation,
    create_branch,
    merge_branch,
    record_change,
    rollback_branch,
)
from memory.failure_frontier import (
    feedback_frontier,
    match_frontiers,
    record_frontier,
)
from memory.utility import feedback_summary, record_feedback, save_receipt


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    os.environ["MEMCODER_FAILURE_FRONTIER_PATH"] = str(root / "frontier.jsonl")
    os.environ["MEMCODER_COGNITIVE_BRANCH_PATH"] = str(root / "branches.jsonl")
    os.environ["MEMCODER_UTILITY_PATH"] = str(root / "utility.jsonl")

    frontier = record_frontier(
        trigger="schema migration",
        risk="stale index",
        warning="The target index may not match the current schema.",
        verification="Run the migration test against a disposable database.",
        owner="beta26",
        counterexamples=["migration already applied"],
    )
    assert match_frontiers("schema migration index", owner="beta26")[0]["id"] == frontier["id"]
    feedback_frontier(frontier["id"], "harmful", owner="beta26")
    assert not match_frontiers("schema migration index", owner="beta26")

    branch = create_branch("calibration", owner="beta26", project_id="demo")
    branch = record_change(branch["id"], "belief", "retrieval.threshold", after=0.62, owner="beta26")
    obligation = add_proof_obligation(branch["id"], "focused regression", owner="beta26")
    assert not merge_branch(branch["id"], owner="beta26")["merge_allowed"]
    obligation_id = obligation["proof_obligations"][-1]["id"]
    branch = complete_proof_obligation(
        branch["id"], obligation_id, True, {"command": "python test"}, owner="beta26"
    )
    assert cognitive_diff(branch["id"], owner="beta26")["change_count"] == 1
    assert merge_branch(branch["id"], owner="beta26")["merge_allowed"]
    assert merge_branch(branch["id"], owner="beta26", apply=True)["status"] == "merged"
    assert rollback_branch(branch["id"], owner="beta26")["status"] == "rolled_back"

    receipt = save_receipt({"id": "intervention_beta26", "memory_ids": ["memory-1"]}, "beta26")
    record_feedback("intervention_beta26", "helpful", owner="beta26")
    summary = feedback_summary("memory-1", owner="beta26")
    assert summary["recommendation"] == "retain"
    assert summary["counts"]["helpful"] == 1

print("PASS: beta 2.6 cognition")
