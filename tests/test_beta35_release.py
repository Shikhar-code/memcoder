"""Beta 3.5 retrieves locally, explains decisions, and upgrades additively."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from memory.brief import build_decision_brief
from memory.benchmark import run_benchmark
from memory.contracts import host_manifest
from memory.evaluation import evaluate_runs
from memory.hierarchical_search import hierarchical_search
from memory.record_store import lexical_status, save_record, search_records_lexical
from memory.storage_ops import upgrade_storage
from memcoder.cli import main


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    environment = {
        "MEMCODER_RECORD_DB_PATH": str(root / "records.sqlite3"),
        "MEMCODER_DB_PATH": str(root / "chroma"),
        "MEMCODER_UTILITY_PATH": str(root / "utility.jsonl"),
    }
    with patch.dict(os.environ, environment, clear=False):
        memory = save_record({
            "task": "Fix webhook endpoint validation before normalization",
            "files": ["webhook.py"],
            "summary": "The endpoint value was normalized before its type was checked.",
            "solution": "Validate endpoint_name is a non-empty string before calling strip().",
            "type": "experience",
            "owner": "beta35",
            "verification": '{"qa_verdict":"approved","verification_playbook":[{"command":"python test_webhook.py"}]}',
        })

        lexical = search_records_lexical(
            "Fix webhook endpoint_name validation safely",
            owner="beta35",
            include_shared=False,
            record_type="experience",
        )
        assert lexical and lexical[0]["id"] == memory["record_id"]
        assert lexical[0]["retrieval_backend"] == "lexical"
        assert lexical_status()["backend"] in {"sqlite_fts5", "sqlite_like"}

        results = hierarchical_search(
            "Fix webhook endpoint_name validation safely",
            agent_id="beta35",
            include_shared=False,
            environment={"project_id": "release-test"},
        )
        assert results["retrieval"]["backend"] == "lexical"
        assert results["retrieval"]["fallback"] == "semantic_cold"
        assert results["strategy"] == "memory_guided"

        brief = build_decision_brief("Fix webhook validation", results)
        card = brief["decision_card"]
        assert card["recommendation"].startswith("Validate endpoint_name")
        assert card["verification"].startswith("Run:")
        assert card["do_not_apply_when"]
        assert brief["budget"]["within_budget"]

        dry_run = upgrade_storage(dry_run=True)
        assert dry_run["plan"]["authoritative_records_changed"] is False
        upgraded = upgrade_storage()
        assert upgraded["validated"] is True
        assert upgraded["after"]["records"] == 1
        assert Path(upgraded["backup"]).exists()

        assert main([
            "setup", "--all",
            "--policy", str(root / "policy.json"),
            "--project", str(root),
            "--agy-config", str(root / "agy.json"),
            "--claude-config", str(root / "claude.json"),
        ]) == 0
        assert (root / "agy.json").exists()
        assert (root / "claude.json").exists()
        assert "memcoder_autopilot" in (root / "CLAUDE.md").read_text(encoding="utf-8")

manifest = host_manifest("codex")
assert manifest["schema_version"] == 3
assert "lexical_failover" in manifest["capabilities"]
assert "actionable_decision_cards" in manifest["capabilities"]

runs = []
for index in range(24):
    runs.extend([
        {"task_id": f"release-{index}", "condition": "baseline", "passed": True},
        {
            "task_id": f"release-{index}",
            "condition": "memory_guided",
            "passed": True,
            "retrieval_relevant": True,
            "abstention_correct": True,
            "harmful": False,
            "host_blocked": False,
            "guidance_used": True,
            "changed_action": index % 2 == 0,
            "latency_ms": 120,
            "guidance_tokens": 120,
            "estimated_tokens_avoided": 300,
        },
    ])
assert evaluate_runs(runs)["release_readiness"]["ready"] is True

benchmark = run_benchmark(iterations=2)
assert benchmark["lexical_fallback"]["interventions"] == 2
assert benchmark["lexical_fallback"]["within_150ms"] is True

print("PASS: beta 3.5 release cognition")
