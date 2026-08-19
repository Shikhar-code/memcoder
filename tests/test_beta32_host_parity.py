"""Beta 3.2 host setup and lifecycle certification stay deterministic."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from memcoder.cli import (
    configure_agy,
    configure_claude,
    install_claude_instructions,
)
from memory.contracts import certify_host, host_manifest
from memory.service import host_summary


with TemporaryDirectory() as directory:
    root = Path(directory)
    config = root / "mcp.json"
    config.write_text(
        json.dumps({"mcpServers": {"other": {"command": "other"}}}),
        encoding="utf-8",
    )

    result = configure_claude(config, sys.executable)
    updated = json.loads(config.read_text(encoding="utf-8"))
    assert result["changed"] is True
    assert updated["mcpServers"]["other"] == {"command": "other"}
    assert updated["mcpServers"]["memcoder"]["args"] == ["-m", "adapters.mcp.server"]
    assert (root / "mcp.json.bak").exists()
    assert configure_claude(config, sys.executable)["changed"] is False

    instructions = install_claude_instructions(root)
    assert instructions["changed"] is True
    assert install_claude_instructions(root)["changed"] is False
    assert "memcoder_autopilot" in (root / "CLAUDE.md").read_text(encoding="utf-8")

    agy_config = root / "agy.json"
    configure_agy(agy_config, sys.executable)
    assert json.loads(agy_config.read_text(encoding="utf-8"))["mcpServers"]["memcoder"]

manifest = host_manifest("claude")
assert manifest["schema_version"] == 2
assert "verification_finished" in manifest["lifecycle"]
assert "outcome_closure" in manifest["capabilities"]
assert {item["host"] for item in host_summary()} == {"codex", "agy", "claude"}

events = [
    {
        "schema_version": 2,
        "host": "claude",
        "event_id": "event-1",
        "event": "task_started",
        "token_budget": 300,
        "fail_open": False,
        "privacy_safe": True,
    },
    {
        "schema_version": 2,
        "host": "claude",
        "event_id": "event-2",
        "event": "verification_finished",
        "token_budget": 300,
        "fail_open": False,
        "privacy_safe": True,
        "capture": {
            "qa": {"approved": True},
            "outcome_loop": {
                "outcome_id": "outcome-1",
                "prediction_status": "confirmed",
            },
        },
    },
]
assert certify_host("claude", events, strict=True)["certified"] is True
events[1]["event_id"] = "event-1"
assert certify_host("claude", events, strict=True)["certified"] is False

print("PASS: beta 3.2 host parity")
