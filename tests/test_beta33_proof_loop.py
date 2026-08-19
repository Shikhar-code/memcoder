"""Beta 3.3 closes verified intervention predictions exactly once."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from api.cognition import autopilot_event_cognition
from memory.autopilot import begin_event, finish_event, lifecycle_events
from memory.contracts import certify_host
from memory.utility import close_intervention, outcome_summary, save_receipt


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    os.environ["MEMCODER_AUTOPILOT_PATH"] = str(root / "autopilot.jsonl")
    os.environ["MEMCODER_UTILITY_PATH"] = str(root / "utility.jsonl")

    receipt = {
        "id": "intervention-beta33",
        "memory_ids": ["memory-validation"],
        "expected_value": 0.82,
        "decision_changed": "Inspect the verified validation procedure first.",
        "verification": "Run the focused validation test.",
    }
    save_receipt(receipt, "claude", environment={"project_id": "proof-loop"})
    closed = close_intervention(
        receipt["id"],
        {
            "guidance_used": True,
            "changed_action": True,
            "verification_passed": True,
            "evidence": {"command": "python test_validation.py", "exit_code": 0},
            "rework_count": 0,
            "host_tokens": 140,
        },
        owner="claude",
        environment={"project_id": "proof-loop"},
    )
    assert closed["rating"] == "helpful"
    assert closed["prediction_status"] == "confirmed"
    assert closed["calibrated"] is True
    assert close_intervention(
        receipt["id"],
        {"guidance_used": True, "changed_action": True, "verification_passed": True},
        owner="claude",
    )["deduplicated"] is True
    assert outcome_summary(owner="claude")["counts"]["confirmed"] == 1

    save_receipt({"id": "intervention-ignored", "memory_ids": []}, "claude")
    ignored = close_intervention(
        "intervention-ignored",
        {"guidance_used": False},
        owner="claude",
    )
    assert ignored["rating"] == "ignored"
    save_receipt({"id": "intervention-unknown", "memory_ids": []}, "claude")
    unknown = close_intervention(
        "intervention-unknown",
        {"guidance_used": True, "verification_passed": False},
        owner="claude",
    )
    assert unknown["rating"] is None
    assert unknown["calibrated"] is False

    api_receipt = {"id": "intervention-api", "memory_ids": [], "expected_value": 0.7}
    save_receipt(api_receipt, "claude")
    with patch("api.cognition.intervene_cognition", return_value={
        "intervention": {"mode": "brief"},
        "receipt": api_receipt,
        "budget": {"estimated_tokens": 80},
    }), patch("api.cognition.record_cognition", return_value={
        "experience_recorded": True,
        "recorded": {"experience": {"id": "record-api"}, "reflections": []},
        "qa": {"approved": True},
        "rejected": [],
    }), patch("memory.dreaming.run_dream", return_value={"created": []}):
        autopilot_event_cognition(
            event="task_started",
            task_id="task-api",
            problem="Fix the request validation guard.",
            agent_id="claude",
            host="claude",
        )
        api_finished = autopilot_event_cognition(
            event="verification_finished",
            task_id="task-api",
            problem="The request validation guard passed its focused check.",
            agent_id="claude",
            host="claude",
            outcome={
                "task": "Fix the request validation guard.",
                "files": ["request.py"],
                "summary": "The guard passed the focused check.",
                "solution": "Validated the field before processing.",
                "evidence": {"command": "python test_request.py", "exit_code": 0},
                "guidance_used": True,
                "changed_action": True,
                "verification_passed": True,
            },
        )
    assert api_finished["capture"]["outcome_loop"]["rating"] == "helpful"
    assert certify_host("claude", lifecycle_events("claude", "task-api"), strict=True)["certified"]

    start = begin_event(
        "task_started",
        "task-proof-loop",
        "claude",
        "Fix the required request field validation.",
        environment={"available_checks": ["python test_validation.py"]},
    )
    first = finish_event(
        start,
        intervention={
            "intervention": {"mode": "brief"},
            "receipt": {"id": receipt["id"]},
            "budget": {"estimated_tokens": 90},
        },
        token_budget=300,
        host="claude",
    )
    assert first["host"] == "claude"
    verify = begin_event(
        "verification_finished",
        "task-proof-loop",
        "claude",
        "The validation test passed after the request guard was added.",
        environment={"available_checks": ["python test_validation.py"]},
    )
    loop = close_intervention(
        receipt["id"],
        {
            "guidance_used": True,
            "changed_action": True,
            "verification_passed": True,
            "evidence": {"command": "python test_validation.py", "exit_code": 0},
        },
        owner="claude",
    )
    finished = finish_event(
        verify,
        capture={"qa": {"approved": True}, "outcome_loop": loop},
        token_budget=300,
        host="claude",
    )
    certified = certify_host("claude", lifecycle_events("claude", "task-proof-loop"), strict=True)
    assert certified["certified"] is True
    assert finished["schema_version"] == 2

    del os.environ["MEMCODER_AUTOPILOT_PATH"]
    del os.environ["MEMCODER_UTILITY_PATH"]

print("PASS: beta 3.3 adaptive proof loop")
