"""The project knowledge contract must make host calls deterministic."""

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.append(str(Path(__file__).resolve().parents[1]))

from memcoder import cli
from memory.knowledge import configure_knowledge, load_knowledge_config


def run_command(arguments):
    output = io.StringIO()
    with redirect_stdout(output):
        code = cli.main(arguments)
    return code, json.loads(output.getvalue())


with TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    source = directory / "knowledge" / "bio"
    source.mkdir(parents=True)
    (source / "scene_rules.md").write_text(
        "# Scene rules\n\nUse high contrast labels.", encoding="utf-8"
    )
    config_path = directory / ".memcoder" / "knowledge.json"

    configured = configure_knowledge(
        source_root=source.parent,
        agent_id="lesson-video-pipeline",
        config_path=config_path,
        include_shared=False,
    )
    assert configured["config_path"] == str(config_path.resolve())
    assert configured["agent_id"] == "lesson-video-pipeline"

    config = load_knowledge_config(config_path)
    assert config["source_root"] == str(source.resolve())
    assert config["include_shared"] is False
    assert config["include_knowledge"] is True

    calls = {}

    def sync_knowledge(source_root):
        calls["sync_source"] = source_root
        return {"files_indexed": 1, "chunks_indexed": 1}

    def knowledge_status(source_root=None):
        calls["status_source"] = source_root
        return {"files": 1, "chunks": 1}

    def prepare_cognition(**kwargs):
        calls["prepare"] = kwargs
        return {"strategy": "normal_reasoning", "knowledge": []}

    cli.sync_knowledge = sync_knowledge
    cli.knowledge_status = knowledge_status
    cli.prepare_cognition = prepare_cognition

    code, output = run_command(["knowledge", "sync", "--config", str(config_path)])
    assert code == 0
    assert output["chunks_indexed"] == 1
    assert calls["sync_source"] == str(source.resolve())

    code, output = run_command(["knowledge", "status", "--config", str(config_path)])
    assert code == 0
    assert output["chunks"] == 1
    assert calls["status_source"] == str(source.resolve())

    request_path = directory / "prepare.json"
    request_path.write_text(
        json.dumps({"problem": "Plan a readable Biology scene.", "subject": "bio"}),
        encoding="utf-8",
    )
    code, output = run_command([
        "prepare", "--config", str(config_path), "--input", str(request_path)
    ])
    assert code == 0
    assert output["strategy"] == "normal_reasoning"
    assert calls["prepare"] == {
        "problem": "Plan a readable Biology scene.",
        "agent_id": "lesson-video-pipeline",
        "include_shared": False,
        "include_knowledge": True,
        "subject": "bio",
    }


print("PASS: project knowledge configuration")
