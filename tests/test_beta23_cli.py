import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from memcoder import cli


calls = {}
cli.utility_feedback_cognition = lambda **kwargs: calls.update(feedback=kwargs) or {"rating": kwargs["rating"]}
cli.retrieval_debug_cognition = lambda **kwargs: calls.update(debug=kwargs) or {"strategy": "normal_reasoning"}
cli.project_update_cognition = lambda **kwargs: calls.update(update=kwargs) or {"id": "state-1"}
cli.project_resurrect_cognition = lambda **kwargs: calls.update(resurrect=kwargs) or {"status": "ready"}
cli.project_handoff_cognition = lambda **kwargs: calls.update(handoff=kwargs) or {"kind": "memcoder_project_handoff"}
cli.project_accept_cognition = lambda **kwargs: calls.update(accept=kwargs) or {"accepted": True}


def run(command, request, directory):
    path = Path(directory) / f"{command}.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    output = io.StringIO()
    with redirect_stdout(output):
        code = cli.main([command, "--input", str(path)])
    return code, json.loads(output.getvalue())


with TemporaryDirectory() as directory:
    base = {"agent_id": "codex", "environment": {"project_id": "memcoder"}}
    assert run("utility-feedback", {**base, "intervention_id": "i-1", "rating": "helpful"}, directory)[0] == 0
    assert calls["feedback"]["rating"] == "helpful"
    assert run("retrieval-debug", {**base, "problem": "Fix validation"}, directory)[1]["strategy"] == "normal_reasoning"
    assert run("project-update", {**base, "project_id": "memcoder", "update": {"facts": []}}, directory)[1]["id"] == "state-1"
    assert run("project-resurrect", {**base, "project_id": "memcoder"}, directory)[1]["status"] == "ready"
    capsule = run("project-handoff", {**base, "project_id": "memcoder"}, directory)[1]
    assert run("project-accept", {**base, "capsule": capsule}, directory)[1]["accepted"]

print("PASS: beta 2.3 CLI surfaces")
