"""Beta 2.5 CLI exposes Dreaming and cognition contract checks."""

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


with patch("memcoder.cli.dream_cognition", return_value={"automatic": True}) as mocked:
    assert run("dream", {"action": "run"}) == 0
    assert mocked.call_count == 1

assert run("contract", {
    "contract": {"name": "proof", "assertions": [{"rule": "requires_verification"}]},
    "observations": {"verification_required": True},
}) == 0

assert run("host-certify", {
    "host": "test-host",
    "events": [
        {"event": "task_started", "fail_open": False},
        {"event": "verification_finished", "fail_open": False, "capture": {"qa": {"approved": True}}},
    ],
}) == 0

print("PASS: beta 2.5 CLI")
