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
storage_calls = {}


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


def migrate_legacy_chroma(collection):
    storage_calls["migrate"] = collection
    return {"migrated": 3, "already_migrated": False}


def migrate_legacy_workspace_storage():
    storage_calls["workspace_migration"] = True
    return {"already_migrated": False, "records": 3, "edges": 2, "audits": 1}


def rebuild_guidance_index(collection, embed):
    storage_calls["rebuild"] = (collection, embed)
    return {"indexed": 3, "removed": 4}


def backfill_existing_provenance():
    storage_calls["provenance"] = True
    return {"processed": 3, "links_considered": 2}


def storage_status():
    return {"records": 3, "provenance_edges": 2, "plan_audits": 1}


def export_snapshot(output):
    storage_calls["export"] = output
    return {"path": str(output), "records": 3}


def create_backup(output):
    storage_calls["backup"] = output
    return {"path": str(output or "automatic.zip"), "records": 3, "format": "zip"}


def restore_snapshot(input):
    storage_calls["restore"] = input
    return {"mode": "merge", "records_merged": 3}


def retention_preview(owner=None):
    storage_calls["retention_preview"] = owner
    return {"schema_version": 1, "actions": [], "safe_to_apply": False}


def apply_retention_preview(preview, owner=None):
    storage_calls["retention_apply"] = (preview, owner)
    return {"mode": "state_transition_only", "applied": [], "deleted": []}


cli.migrate_legacy_chroma = migrate_legacy_chroma
cli.migrate_legacy_workspace_storage = migrate_legacy_workspace_storage
cli.rebuild_guidance_index = rebuild_guidance_index
cli.backfill_existing_provenance = backfill_existing_provenance
cli.storage_status = storage_status
cli.export_snapshot = export_snapshot
cli.create_backup = create_backup
cli.restore_snapshot = restore_snapshot
cli.retention_preview = retention_preview
cli.apply_retention_preview = apply_retention_preview


def run_command(arguments):
    output = io.StringIO()
    with redirect_stdout(output):
        code = cli.main(arguments)
    return code, json.loads(output.getvalue())


with TemporaryDirectory() as storage_directory:
    directory = Path(storage_directory)
    code, output = run_command(["storage", "migrate"])
    assert code == 0
    assert output["storage"]["migration"]["migrated"] == 3
    assert output["storage"]["provenance"]["processed"] == 3

    code, output = run_command(["storage", "rebuild-index"])
    assert code == 0
    assert output["storage"]["index"] == {"indexed": 3, "removed": 4}

    code, output = run_command(["storage", "status"])
    assert code == 0
    assert output["storage"]["records"] == 3

    export_output = directory / "export.json"
    code, output = run_command(["storage", "export", "--output", str(export_output)])
    assert code == 0
    assert output["storage"]["export"]["records"] == 3

    backup_output = directory / "backup.zip"
    code, output = run_command(["storage", "backup", "--output", str(backup_output)])
    assert code == 0
    assert output["storage"]["backup"]["format"] == "zip"

    code, output = run_command(["storage", "restore", "--input", str(backup_output)])
    assert code == 0
    assert output["storage"]["restore"]["mode"] == "merge"

    code, output = run_command(["storage", "retention-preview", "--owner", "video-pipeline"])
    assert code == 0
    assert output["retention"]["safe_to_apply"] is False
    assert storage_calls["retention_preview"] == "video-pipeline"

    retention_path = directory / "retention.json"
    retention_path.write_text(
        json.dumps({"retention": {"schema_version": 1, "actions": []}}),
        encoding="utf-8",
    )
    code, output = run_command([
        "storage", "retention-apply", "--input", str(retention_path), "--owner", "video-pipeline"
    ])
    assert code == 0
    assert output["retention"]["mode"] == "state_transition_only"


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
