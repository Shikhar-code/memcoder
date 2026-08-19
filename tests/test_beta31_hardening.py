"""Beta 3.1 keeps startup lazy and completion capture idempotent."""

import os
import sys
import tempfile
from unittest.mock import patch


import memory.markdown_import  # noqa: F401


assert "memory.principle_capture" not in sys.modules

with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_AUTOPILOT_PATH"] = os.path.join(directory, "autopilot.jsonl")
    capture = {
        "experience_recorded": True,
        "recorded": {"experience": {"id": "mem-beta31"}, "reflections": []},
        "qa": {"approved": True, "verdict": "approved"},
        "rejected": [],
    }
    with patch("api.cognition.record_cognition", return_value=capture) as record, patch(
            "memory.dreaming.run_dream", return_value={"created": []}):
        from api.cognition import autopilot_event_cognition

        arguments = {
            "event": "verification_finished",
            "task_id": "beta31-task",
            "problem": "Verify a focused change.",
            "agent_id": "beta31",
            "outcome": {
                "task": "Verify a focused change.",
                "files": ["change.py"],
                "summary": "The focused change passed its regression check.",
                "solution": "Ran the targeted regression and retained its output.",
                "evidence": {"checks": [{
                    "name": "focused regression",
                    "kind": "test",
                    "status": "passed",
                    "command": "python test_change.py",
                    "output": "PASS",
                }]},
            },
        }
        first = autopilot_event_cognition(**arguments)
        replay = autopilot_event_cognition(**arguments)

    assert first["capture"]["experience_recorded"]
    assert replay["capture"] == first["capture"]
    assert replay["attention"]["deduplicated"]
    assert record.call_count == 1
    del os.environ["MEMCODER_AUTOPILOT_PATH"]

print("PASS: beta 3.1 hardening")
