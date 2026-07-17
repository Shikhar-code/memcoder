"""JSON automation calls must be provider-free and require verification."""

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.append(str(Path(__file__).resolve().parents[1]))

from memcoder import cli


prepare_calls = {}
record_calls = {}


def prepare_cognition(**kwargs):
    prepare_calls.update(kwargs)
    return {"strategy": "memory_guided", "principles": []}


def record_cognition(**kwargs):
    record_calls.update(kwargs)
    return {"experience_recorded": True, "rejected": []}


cli.prepare_cognition = prepare_cognition
cli.record_cognition = record_cognition


def run_command(arguments):
    output = io.StringIO()
    with redirect_stdout(output):
        code = cli.main(arguments)
    return code, json.loads(output.getvalue())


with TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    prepare_path = directory / "prepare.json"
    prepare_path.write_text(json.dumps({
        "problem": "Plan a verified educational video render.",
        "agent_id": "video-pipeline",
        "include_shared": False
    }), encoding="utf-8")

    code, output = run_command(["prepare", "--input", str(prepare_path)])
    assert code == 0
    assert output["strategy"] == "memory_guided"
    assert prepare_calls == {
        "problem": "Plan a verified educational video render.",
        "agent_id": "video-pipeline",
        "include_shared": False
    }

    record_path = directory / "record.json"
    record_path.write_text(json.dumps({
        "verified": True,
        "task": "Render an educational video.",
        "files": ["outputs/qa_report.json"],
        "summary": "QA and rendering completed successfully.",
        "solution": "Used the approved production path.",
        "agent_id": "video-pipeline"
    }), encoding="utf-8")

    code, output = run_command(["record", "--input", str(record_path)])
    assert code == 0
    assert output["experience_recorded"]
    assert record_calls["agent_id"] == "video-pipeline"

    unverified_path = directory / "unverified.json"
    unverified_path.write_text(json.dumps({
        "task": "Unverified render",
        "files": [],
        "summary": "No proof exists yet.",
        "solution": "Do not store this."
    }), encoding="utf-8")

    code, output = run_command(["record", "--input", str(unverified_path)])
    assert code == 2
    assert output["error"]["code"] == "invalid_request"
    assert record_calls["task"] == "Render an educational video."

print("PASS: provider-free automation CLI")
