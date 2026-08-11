"""Beta 2.6 CLI exposes frontier, calibration, and cognitive-branch controls."""

import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from memcoder.cli import main


def run(command, request):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "request.json"
        path.write_text(json.dumps(request), encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            code = main([command, "--input", str(path)])
        return code, json.loads(output.getvalue())


with patch("memcoder.cli.failure_frontier_cognition", return_value={"matches": []}) as frontier:
    code, result = run("frontier", {"action": "match", "problem": "schema drift"})
    assert code == 0 and result == {"matches": []}
    assert frontier.call_count == 1

with patch("memcoder.cli.cognitive_branch_cognition", return_value={"branches": []}) as branch:
    code, result = run("branch", {"action": "list"})
    assert code == 0 and result == {"branches": []}
    assert branch.call_count == 1

with patch("memcoder.cli.utility_feedback_summary_cognition", return_value={"total": 0}) as summary:
    code, result = run("utility-summary", {})
    assert code == 0 and result == {"total": 0}
    assert summary.call_count == 1

print("PASS: beta 2.6 CLI")
