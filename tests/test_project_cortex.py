import json
import os
import tempfile

from memory.project_cortex import (
    accept_handoff,
    export_handoff,
    resurrect_project,
    update_project_state,
)


with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_PROJECT_STATE_PATH"] = os.path.join(directory, "projects.jsonl")
    environment = {"project_id": "memcoder", "runtime": "python", "branch": "main"}
    stored = update_project_state(
        "memcoder",
        "codex",
        {
            "goals": ["Ship Beta 2.3."],
            "facts": ["Provider-free core is required."],
            "constraints": ["No new dependencies.", "api_key=must-not-leak"],
            "completed_work": ["Beta 2.2 runtime is verified."],
            "risks": ["Stale decisions can mislead a resumed task."],
            "next_actions": ["Run focused Beta 2.3 tests."],
            "important_files": ["memory/runtime.py"],
            "decisions": [{
                "decision": "Use append-only local project state.",
                "rationale": "It matches existing task-state storage.",
                "scope": "project storage",
                "evidence": ["Existing JSONL checkpoint implementation."],
            }],
        },
        environment=environment,
    )
    assert stored["id"].startswith("project_state_")

    recovered = resurrect_project("memcoder", "codex", environment=environment, token_budget=300)
    assert recovered["status"] == "ready"
    assert recovered["brief"]["objective"] == "Ship Beta 2.3."
    assert recovered["brief"]["decisions"]
    assert recovered["budget"]["estimated_tokens"] <= 300

    drifted = resurrect_project(
        "memcoder", "codex", environment={**environment, "runtime": "node"}
    )
    assert drifted["status"] == "drifted"
    assert drifted["brief"]["decisions"] == []
    assert drifted["withheld_decisions"]

    capsule = export_handoff(
        "memcoder",
        "codex",
        environment={**environment, "api_key": "must-not-leak", "raw_transcript": "private"},
    )
    serialized = json.dumps(capsule)
    assert "must-not-leak" not in serialized
    assert "raw_transcript" not in serialized

    accepted = accept_handoff(
        capsule,
        "receiver",
        environment={**environment, "branch": "feature"},
    )
    assert accepted["accepted"]
    assert accepted["environment_delta"]["status"] == "drifted"
    del os.environ["MEMCODER_PROJECT_STATE_PATH"]

print("PASS: project cortex")
