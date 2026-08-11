import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from memcoder.cli import main


def run(command, request):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "request.json"
        path.write_text(json.dumps(request), encoding="utf-8")
        return main([command, "--input", str(path)])


with patch("memcoder.cli.autopilot_event_cognition", return_value={"available": True}) as mocked:
    assert run("autopilot", {
        "event": "task_started",
        "task_id": "task-1",
        "problem": "Fix the current validation bug",
    }) == 0
    assert mocked.call_count == 1

assert run("skill-compile", {
    "problem": "Validate a Python request",
    "definition": {
        "when_to_use": "validating a Python request",
        "steps": ["Inspect input."],
        "verification": ["Run the test."],
    },
}) == 0

print("PASS: beta 2.4 CLI")
