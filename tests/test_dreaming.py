"""Dreaming is automatic, local, and cannot bypass sandbox proof."""

import json
import os
import tempfile
from unittest.mock import patch

from memory.dreaming import evaluate_candidate, list_candidates, rollback_candidate, run_dream


with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_DREAM_PATH"] = os.path.join(directory, "dreams.jsonl")
    records = [
        {
            "record_id": "mem-a", "owner": "tester", "type": "experience",
            "record_state": "trusted", "task": "Validate tenant request input",
            "verification": json.dumps({"qa_verdict": "approved"}),
        },
        {
            "record_id": "mem-b", "owner": "tester", "type": "experience",
            "record_state": "trusted", "task": "Validate webhook request input",
            "verification": json.dumps({"qa_verdict": "approved"}),
        },
    ]
    with patch("memory.dreaming.list_records", return_value=records):
        result = run_dream(owner="tester")
    assert result["automatic"] is True
    assert len(result["created"]) == 1
    candidate_id = result["created"][0]["candidate_id"]
    assert list_candidates("tester")[0]["sandbox"]["status"] == "pending"

    checked = evaluate_candidate(candidate_id, [{
        "name": "held-out validation", "passed": True, "evidence": "test passed",
    }], owner="tester", auto_promote=False)
    assert checked["candidate"]["sandbox"]["status"] == "passed"
    assert checked["promoted"] is None
    try:
        evaluate_candidate(candidate_id, [{"name": "bad"}], owner="tester")
    except ValueError as error:
        assert "passed boolean" in str(error)
    else:
        raise AssertionError("Malformed sandbox evidence must be rejected")

    with patch("memory.capture.capture_memory", return_value={"record_id": "mem-dream"}), \
            patch("memory.provenance.link"):
        promoted = evaluate_candidate(candidate_id, [{
            "name": "repeat held-out validation", "passed": True, "evidence": "second test passed",
        }], owner="tester")
    assert promoted["promoted"]["record_id"] == "mem-dream"
    with patch("memory.validity.set_record_validity") as validity:
        rolled_back = rollback_candidate(candidate_id, owner="tester")
    assert rolled_back["record_id"] == "mem-dream"
    assert validity.call_count == 1
    assert list_candidates("tester")[0]["status"] == "rolled_back"
    try:
        evaluate_candidate(candidate_id, [{
            "name": "stale retry", "passed": True, "evidence": "should be blocked",
        }], owner="tester")
    except ValueError as error:
        assert "no longer eligible" in str(error)
    else:
        raise AssertionError("Rolled-back candidates must not be silently re-promoted")

os.environ.pop("MEMCODER_DREAM_PATH", None)

with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_AUTOPILOT_PATH"] = os.path.join(directory, "autopilot.jsonl")
    with patch("api.cognition.record_cognition", return_value={
        "experience_recorded": True,
        "recorded": {"experience": {"id": "mem-a"}, "reflections": []},
        "qa": {"approved": True},
        "rejected": [],
    }), patch("memory.dreaming.run_dream", return_value={"automatic": True}) as dreamed:
        from api.cognition import autopilot_event_cognition
        receipt = autopilot_event_cognition(
            event="verification_finished",
            task_id="task-1",
            problem="validate a request",
            agent_id="tester",
            outcome={
                "task": "validate a request", "files": ["request.py"],
                "summary": "fixed validation", "solution": "added a guard",
                "evidence": {"checks": []},
            },
        )
    assert receipt["capture"]["dream"]["automatic"] is True
    assert dreamed.call_count == 1

os.environ.pop("MEMCODER_AUTOPILOT_PATH", None)
print("PASS: automatic dreaming and sandbox gate")
