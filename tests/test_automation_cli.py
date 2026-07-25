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
plan_calls = {}
history_calls = {}
health_calls = {}
evaluation_calls = {}
start_calls = {}
record_calls = {}
skill_calls = {}


def prepare_cognition(**kwargs):
    prepare_calls.update(kwargs)
    return {"strategy": "memory_guided", "principles": []}


def plan_cognition(**kwargs):
    plan_calls.update(kwargs)
    return {"plan": {"mode": "foundation", "steps": []}}


def start_cognition(**kwargs):
    start_calls.update(kwargs)
    return {"brief": {}, "plan": {"mode": "foundation", "steps": []}}


def plan_history_cognition(**kwargs):
    history_calls.update(kwargs)
    return {"plan_id": kwargs["plan_id"], "outcomes": []}


def skill_health_cognition(**kwargs):
    health_calls.update(kwargs)
    return {"skill_id": kwargs["skill_id"], "status": "unproven"}


def evaluate_cognition(runs):
    evaluation_calls["runs"] = runs
    return {"conditions": {"baseline": {"runs": len(runs)}}}


def record_cognition(**kwargs):
    record_calls.update(kwargs)
    approved = bool(kwargs["evidence"].get("checks"))
    return {
        "experience_recorded": approved,
        "rejected": [] if approved else ["qa: outcome was not admitted"],
        "qa": {"verdict": "approved" if approved else "insufficient_evidence"}
    }


def promote_skill_cognition(**kwargs):
    skill_calls.update(kwargs)
    return {"promoted": True, "id": "skill-1"}


cli.prepare_cognition = prepare_cognition
cli.plan_cognition = plan_cognition
cli.start_cognition = start_cognition
cli.plan_history_cognition = plan_history_cognition
cli.skill_health_cognition = skill_health_cognition
cli.evaluate_cognition = evaluate_cognition
cli.record_cognition = record_cognition
cli.promote_skill_cognition = promote_skill_cognition


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
        "include_shared": False,
        "detail_level": "brief",
    }), encoding="utf-8")

    code, output = run_command(["prepare", "--input", str(prepare_path)])
    assert code == 0
    assert output["strategy"] == "memory_guided"
    assert prepare_calls == {
        "problem": "Plan a verified educational video render.",
        "agent_id": "video-pipeline",
        "include_shared": False,
        "include_skills": True,
        "detail_level": "brief",
    }

    code, output = run_command(["start", "--input", str(prepare_path)])
    assert code == 0
    assert output["plan"]["mode"] == "foundation"
    assert start_calls == {
        "problem": "Plan a verified educational video render.",
        "agent_id": "video-pipeline",
        "include_shared": False,
    }

    code, output = run_command(["plan", "--input", str(prepare_path)])
    assert code == 0
    assert output["plan"]["mode"] == "foundation"
    assert plan_calls == {
        "problem": "Plan a verified educational video render.",
        "agent_id": "video-pipeline",
        "include_shared": False,
    }

    history_path = directory / "plan-history.json"
    history_path.write_text(json.dumps({
        "plan_id": "plan_1234567890abcdef1234",
        "agent_id": "video-pipeline",
    }), encoding="utf-8")
    code, output = run_command(["plan-history", "--input", str(history_path)])
    assert code == 0
    assert output["outcomes"] == []
    assert history_calls == {
        "plan_id": "plan_1234567890abcdef1234",
        "agent_id": "video-pipeline",
    }

    health_path = directory / "skill-health.json"
    health_path.write_text(json.dumps({
        "skill_id": "skill-1",
        "agent_id": "video-pipeline",
    }), encoding="utf-8")
    code, output = run_command(["skill-health", "--input", str(health_path)])
    assert code == 0
    assert output["status"] == "unproven"
    assert health_calls == {
        "skill_id": "skill-1",
        "agent_id": "video-pipeline",
    }

    evaluation_path = directory / "evaluation.json"
    evaluation_path.write_text(json.dumps({
        "runs": [{"task_id": "task-1", "condition": "baseline", "passed": True}]
    }), encoding="utf-8")
    code, output = run_command(["evaluate", "--input", str(evaluation_path)])
    assert code == 0
    assert output["conditions"]["baseline"]["runs"] == 1
    assert evaluation_calls["runs"][0]["task_id"] == "task-1"

    record_path = directory / "record.json"
    record_path.write_text(json.dumps({
        "task": "Render an educational video.",
        "files": ["outputs/qa_report.json"],
        "summary": "QA and rendering completed successfully.",
        "solution": "Used the approved production path.",
        "evidence": {
            "checks": [{
                "name": "mandatory production QA",
                "kind": "test",
                "status": "passed",
                "command": "python core/quality_assurance.py",
                "output": "PASS: approved"
            }]
        },
        "agent_id": "video-pipeline"
    }), encoding="utf-8")

    code, output = run_command(["record", "--input", str(record_path)])
    assert code == 0
    assert output["experience_recorded"]
    assert record_calls["agent_id"] == "video-pipeline"

    code, output = run_command(["verify", "--input", str(record_path)])
    assert code == 0
    assert output["verdict"] == "approved"

    unverified_path = directory / "unverified.json"
    unverified_path.write_text(json.dumps({
        "task": "Unverified render",
        "files": [],
        "summary": "No proof exists yet.",
        "solution": "Do not store this.",
        "evidence": {"checks": []}
    }), encoding="utf-8")

    code, output = run_command(["record", "--input", str(unverified_path)])
    assert code == 0
    assert output["qa"]["verdict"] == "insufficient_evidence"
    assert not output["experience_recorded"]
    assert record_calls["task"] == "Unverified render"

    skill_path = directory / "skill.json"
    skill_path.write_text(json.dumps({
        "name": "Required field validation",
        "when_to_use": "A required request field may be missing before processing.",
        "inputs": ["request payload"],
        "steps": ["Check the field.", "Run the focused test."],
        "verification": ["Focused test passes."],
        "supporting_experience_ids": ["experience-1", "experience-2"],
        "agent_id": "video-pipeline"
    }), encoding="utf-8")

    code, output = run_command(["skill", "promote", "--input", str(skill_path)])
    assert code == 0
    assert output["promoted"]
    assert skill_calls["supporting_experience_ids"] == ["experience-1", "experience-2"]
    assert skill_calls["supporting_principle_ids"] is None

print("PASS: provider-free automation CLI")
