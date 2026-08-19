"""Small, dependency-free setup commands for MemCoder users."""

import argparse
import json
import shutil
import sys
from pathlib import Path

from api.cognition import (
    autopilot_control_cognition,
    autopilot_event_cognition,
    capsule_cognition,
    certify_host_cognition,
    host_manifest_cognition,
    checkpoint_cognition,
    compile_skill_cognition,
    compose_skills_cognition,
    cognition_contract_cognition,
    dream_cognition,
    doctor_cognition,
    cognitive_branch_cognition,
    evaluate_cognition,
    evolve_skill_cognition,
    failure_frontier_cognition,
    intervene_cognition,
    project_accept_cognition,
    project_handoff_cognition,
    project_resurrect_cognition,
    project_update_cognition,
    retrieval_debug_cognition,
    plan_history_cognition,
    plan_cognition,
    policy_cognition,
    prepare_cognition,
    promote_skill_cognition,
    record_cognition,
    replay_cognition,
    skill_health_cognition,
    skill_credit_cognition,
    start_cognition,
    task_state_cognition,
    token_ledger_cognition,
    utility_feedback_cognition,
    utility_feedback_summary_cognition,
    verify_cognition,
)
from memory.chroma_client import collection
from memory.record_store import (
    migrate_legacy_chroma,
    migrate_legacy_workspace_storage,
    rebuild_guidance_index,
)
from memory.provenance import backfill_existing_provenance
from memory.storage_ops import (
    create_backup,
    export_snapshot,
    restore_snapshot,
    storage_status,
)
from memory.retention import apply_retention_preview, retention_preview
from memory.contradictions import report_contradiction, resolve_contradiction


def default_agy_config_path():
    """Return AGY's per-user MCP configuration path."""
    return Path.home() / ".gemini" / "antigravity" / "mcp_config.json"


def default_claude_config_path():
    """Return Claude Code's project-scoped MCP configuration path."""
    return Path.cwd() / ".mcp.json"


def _load_mcp_config(config_path, host):
    config_path = Path(config_path)
    if not config_path.exists():
        return config_path, {}
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Cannot update invalid JSON configuration: {config_path}") from error
    if not isinstance(config, dict):
        raise ValueError(f"{host} MCP configuration must contain a JSON object.")
    return config_path, config


def _write_mcp_config(config_path, config):
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    new_text = json.dumps(config, indent=2) + "\n"
    old_text = config_path.read_text(encoding="utf-8") if config_path.exists() else None
    if old_text == new_text:
        return {"path": str(config_path), "changed": False, "backup": None}
    backup = None
    if old_text is not None:
        backup_path = config_path.with_suffix(config_path.suffix + ".bak")
        backup_path.write_text(old_text, encoding="utf-8")
        backup = str(backup_path)
    config_path.write_text(new_text, encoding="utf-8")
    return {"path": str(config_path), "changed": True, "backup": backup}


def configure_agy(config_path, python_executable):
    """Add or update MemCoder without disturbing other MCP servers."""
    config_path, config = _load_mcp_config(config_path, "AGY")

    servers = config.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError("AGY MCP configuration field 'mcpServers' must be an object.")

    servers["memcoder"] = {
        "command": str(Path(python_executable).resolve()),
        "args": ["-m", "adapters.mcp.server"]
    }

    _write_mcp_config(config_path, config)
    return config_path


def configure_claude(config_path, python_executable):
    """Add or update MemCoder in Claude Code's project MCP configuration."""
    config_path, config = _load_mcp_config(config_path, "Claude Code")
    servers = config.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError("Claude Code MCP configuration field 'mcpServers' must be an object.")
    servers["memcoder"] = {
        "command": str(Path(python_executable).resolve()),
        "args": ["-m", "adapters.mcp.server"],
    }
    return _write_mcp_config(config_path, config)


CLAUDE_INSTRUCTIONS = """<!-- memcoder:start -->
## MemCoder cognition

For substantive development tasks, use the configured MemCoder MCP server's
`memcoder_autopilot` lifecycle. Start with `task_started`, treat returned
guidance as a hypothesis, verify the host's work normally, and send the actual
verification result at `verification_finished`. Use project resurrection when
resuming known work. MemCoder is provider-free, fail-open, and must never be
treated as proof without current host verification. Do not record an outcome
when the fix or verification failed.
At `verification_finished`, include explicit outcome fields when available:
`guidance_used`, `changed_action`, `verification_passed`, `evidence`,
`rework_count`, and `host_tokens`. MemCoder calibrates only from this
host-supplied proof.
<!-- memcoder:end -->
"""


def install_claude_instructions(project_path):
    """Install one idempotent project instruction block for Claude Code."""
    project_path = Path(project_path).resolve()
    target = project_path / "CLAUDE.md"
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    start = "<!-- memcoder:start -->"
    end = "<!-- memcoder:end -->"
    if start in existing and end in existing:
        prefix, _, remainder = existing.partition(start)
        _, _, suffix = remainder.partition(end)
        updated = prefix + CLAUDE_INSTRUCTIONS.rstrip() + suffix
        if updated == existing:
            return {"path": str(target), "changed": False}
        target.write_text(updated, encoding="utf-8")
        return {"path": str(target), "changed": True, "updated": True}
    separator = "\n\n" if existing.strip() else ""
    target.write_text(existing.rstrip() + separator + CLAUDE_INSTRUCTIONS + "\n", encoding="utf-8")
    return {"path": str(target), "changed": True}


def load_json_request(input_path):
    """Load one JSON-object request from a file or standard input."""
    try:
        raw = sys.stdin.read() if str(input_path) == "-" else Path(input_path).read_text(
            encoding="utf-8-sig"
        )
        request = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read JSON request: {error}") from error

    if not isinstance(request, dict):
        raise ValueError("JSON request must be an object.")

    return request


def require_text(request, field):
    value = request.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Request field '{field}' must be a non-empty string.")
    return value.strip()


def emit_json(payload):
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="memcoder")
    subcommands = parser.add_subparsers(dest="command", required=True)

    setup_agy = subcommands.add_parser(
        "setup-agy",
        help="Configure AGY to use this exact Python installation of MemCoder."
    )
    setup_agy.add_argument(
        "--config",
        type=Path,
        default=default_agy_config_path(),
        help="Override AGY's MCP config path."
    )
    setup_claude = subcommands.add_parser(
        "setup-claude",
        help="Configure Claude Code's project MCP server and lifecycle instructions."
    )
    setup_claude.add_argument(
        "--config",
        type=Path,
        default=default_claude_config_path(),
        help="Override Claude Code's .mcp.json path."
    )
    setup_claude.add_argument(
        "--project",
        type=Path,
        default=Path.cwd(),
        help="Project root where CLAUDE.md instructions are installed."
    )

    setup = subcommands.add_parser(
        "setup",
        help="Create or inspect the safe local Beta 3 configuration.",
    )
    setup.add_argument("--policy", type=Path, help="Override the local policy path.")
    doctor = subcommands.add_parser("doctor", help="Check local storage, policy, and journal health.")
    doctor.add_argument("--host", choices=("codex", "agy", "claude"))
    doctor.add_argument("--config", type=Path, help="Override the selected host's config path.")
    host_manifest = subcommands.add_parser(
        "host-manifest", help="Show the canonical lifecycle contract for a supported host."
    )
    host_manifest.add_argument("--host", required=True, choices=("codex", "agy", "claude"))
    service = subcommands.add_parser("service", help="Run or inspect the localhost cognition service.")
    service.add_argument("action", choices=("doctor", "serve"), default="doctor")
    service.add_argument("--host", default="127.0.0.1")
    service.add_argument("--port", type=int, default=8765)
    studio = subcommands.add_parser("studio", help="Serve the minimal local Memory Studio.")
    studio.add_argument("--host", default="127.0.0.1")
    studio.add_argument("--port", type=int, default=8765)

    storage_command = subcommands.add_parser(
        "storage",
        help="Migrate or rebuild MemCoder's local durable memory storage.",
    )
    storage_subcommands = storage_command.add_subparsers(
        dest="storage_command", required=True
    )
    storage_subcommands.add_parser(
        "migrate",
        help="Copy legacy Chroma-only guidance records into the durable local store.",
    )
    storage_subcommands.add_parser(
        "rebuild-index",
        help="Rebuild the semantic retrieval index from the durable local store.",
    )
    storage_subcommands.add_parser(
        "status",
        help="Show durable-record, provenance, and audit counts without changing data.",
    )
    storage_export = storage_subcommands.add_parser(
        "export",
        help="Write a portable JSON export of local MemCoder cognition.",
    )
    storage_export.add_argument("--output", required=True, type=Path)
    storage_backup = storage_subcommands.add_parser(
        "backup",
        help="Create a timestamped portable backup archive.",
    )
    storage_backup.add_argument("--output", type=Path)
    storage_restore = storage_subcommands.add_parser(
        "restore",
        help="Merge a portable backup, then rebuild the retrieval index.",
    )
    storage_restore.add_argument("--input", required=True, type=Path)
    retention_preview_command = storage_subcommands.add_parser(
        "retention-preview",
        help="Preview safe exact-duplicate retention actions without changing memory.",
    )
    retention_preview_command.add_argument("--owner")
    retention_apply = storage_subcommands.add_parser(
        "retention-apply",
        help="Apply a reviewed retention preview; records are never deleted.",
    )
    retention_apply.add_argument("--input", required=True, type=Path)
    retention_apply.add_argument("--owner")
    contradiction_report = storage_subcommands.add_parser(
        "contradiction-report",
        help="Record conflicting evidence and withhold both memories from automatic reuse.",
    )
    contradiction_report.add_argument("--input", required=True, type=Path)
    contradiction_resolve = storage_subcommands.add_parser(
        "contradiction-resolve",
        help="Resolve reviewed conflicting evidence without deleting either record.",
    )
    contradiction_resolve.add_argument("--input", required=True, type=Path)

    for command, help_text in (
            ("intervene", "Return the smallest useful cognition packet for a task."),
            ("autopilot", "Handle one provider-neutral host lifecycle event."),
            ("autopilot-control", "Pause, inspect, resume, or roll back automatic cognition."),
            ("dream", "Run or inspect automatic evidence-gated Dreaming."),
            ("contract", "Evaluate a deterministic cognition contract."),
            ("host-certify", "Certify a host lifecycle and QA receipt contract."),
            ("token-ledger", "Inspect lifecycle cognition token accounting."),
            ("skill-compile", "Compile safe skill transfer for the current context."),
            ("skill-compose", "Check and order a compatible skill composition."),
            ("skill-evolve", "Create a reviewable next skill version."),
            ("skill-credit", "Record whether a skill actually changed behavior."),
            ("utility-feedback", "Rate the decision utility of one exact intervention."),
            ("utility-summary", "Summarize observed intervention outcomes for calibration."),
            ("frontier", "Record or retrieve verified failure-frontier warnings."),
            ("branch", "Manage proof-gated branch-local cognition and diffs."),
            ("retrieval-debug", "Explain semantic rank, utility rank, and withheld guidance."),
            ("checkpoint", "Save bounded working state without creating memory."),
            ("task-state", "Read the latest owner-scoped working checkpoint."),
            ("project-update", "Update bounded durable project state and decisions."),
            ("project-resurrect", "Recover a bounded project continuation brief."),
            ("project-handoff", "Export a safe project cognition capsule."),
            ("project-accept", "Accept and revalidate a project cognition capsule."),
            ("start", "Retrieve a compact brief and bounded plan in one call."),
            ("plan-history", "Read owner-scoped audit outcomes for one plan."),
            ("skill-health", "Read owner-scoped health for one promoted skill."),
            ("evaluate", "Summarize explicit baseline and MemCoder-assisted runs."),
            ("prepare", "Retrieve provider-free cognition from a JSON request."),
            ("plan", "Build a bounded provider-free plan from a JSON request."),
            ("verify", "Evaluate supplied host verification evidence without storing memory."),
            ("record", "QA and store an outcome only when its evidence is admitted.")):
        subcommand = subcommands.add_parser(command, help=help_text)
        subcommand.add_argument(
            "--input",
            required=True,
            help="Path to a JSON request file, or '-' to read standard input."
        )

    for command, help_text in (
            ("policy", "Inspect or evaluate Memory Firewall rules."),
            ("capsule", "Create, verify, inspect, or import a cognition capsule."),
            ("replay", "Compare captured cognition conditions deterministically.")):
        subcommand = subcommands.add_parser(command, help=help_text)
        subcommand.add_argument(
            "--input",
            required=True,
            help="Path to a JSON request file, or '-' to read standard input."
        )

    skill_command = subcommands.add_parser(
        "skill",
        help="Promote QA-supported experiences into reusable skills."
    )
    skill_subcommands = skill_command.add_subparsers(dest="skill_command", required=True)
    skill_promote = skill_subcommands.add_parser(
        "promote",
        help="Promote one structured skill from QA-approved supporting experiences."
    )
    skill_promote.add_argument(
        "--input",
        required=True,
        help="Path to a JSON request file, or '-' to read standard input."
    )

    arguments = parser.parse_args(argv)

    if arguments.command == "setup-agy":
        try:
            config_path = configure_agy(arguments.config, sys.executable)
        except ValueError as error:
            parser.error(str(error))

        print(f"MemCoder configured for AGY: {config_path}")
        print("Restart AGY. No plugin install command is required.")
        return 0

    if arguments.command == "setup-claude":
        try:
            config = configure_claude(arguments.config, sys.executable)
            instructions = install_claude_instructions(arguments.project)
        except ValueError as error:
            parser.error(str(error))
        emit_json({"host": "claude", "mcp": config, "instructions": instructions})
        print("Restart Claude Code in the configured project.")
        return 0

    if arguments.command == "setup":
        from memory.policy import load_policy, save_policy, policy_status
        target = arguments.policy
        status = policy_status(target)
        if not status["exists"]:
            status["created"] = save_policy(load_policy(target), target)
        else:
            status["created"] = None
        emit_json({"setup": status})
        return 0

    if arguments.command == "doctor":
        result = doctor_cognition()
        if arguments.host:
            config_path = arguments.config
            if config_path is None:
                config_path = {
                    "agy": default_agy_config_path(),
                    "claude": default_claude_config_path(),
                    "codex": Path("codex-marketplace/plugins/memcoder/.mcp.json"),
                }[arguments.host]
            try:
                path, config = _load_mcp_config(config_path, arguments.host)
                server = (config.get("mcpServers") or {}).get("memcoder")
                command = server.get("command") if isinstance(server, dict) else None
                result["host"] = {
                    "name": arguments.host,
                    "config": str(path),
                    "configured": isinstance(server, dict)
                    and server.get("args") == ["-m", "adapters.mcp.server"]
                    and bool(command)
                    and (Path(command).exists() or shutil.which(command)),
                    "command": command,
                    "manifest": host_manifest_cognition(arguments.host),
                }
            except ValueError as error:
                result["host"] = {"name": arguments.host, "configured": False, "error": str(error)}
        emit_json(result)
        return 0

    if arguments.command == "host-manifest":
        emit_json(host_manifest_cognition(arguments.host))
        return 0

    if arguments.command == "service":
        if arguments.action == "doctor":
            emit_json(doctor_cognition())
        else:
            from memory.service import run_server
            run_server(host=arguments.host, port=arguments.port)
        return 0

    if arguments.command == "studio":
        from memory.service import run_server
        run_server(host=arguments.host, port=arguments.port)
        return 0

    if arguments.command == "storage":
        if arguments.storage_command == "status":
            emit_json({"storage": storage_status()})
            return 0
        if arguments.storage_command == "retention-preview":
            emit_json({"retention": retention_preview(owner=arguments.owner)})
            return 0
        if arguments.storage_command == "retention-apply":
            try:
                preview = load_json_request(arguments.input)
                if isinstance(preview.get("retention"), dict):
                    preview = preview["retention"]
                result = apply_retention_preview(preview, owner=arguments.owner)
            except ValueError as error:
                parser.error(str(error))
            emit_json({"retention": result})
            return 0
        if arguments.storage_command in {"contradiction-report", "contradiction-resolve"}:
            try:
                request = load_json_request(arguments.input)
                owner = require_text(request, "owner")
                reason = require_text(request, "reason")
                if arguments.storage_command == "contradiction-report":
                    result = report_contradiction(
                        require_text(request, "first_id"),
                        require_text(request, "second_id"),
                        owner=owner,
                        reason=reason,
                    )
                else:
                    result = resolve_contradiction(
                        require_text(request, "winner_id"),
                        require_text(request, "loser_id"),
                        owner=owner,
                        reason=reason,
                    )
            except ValueError as error:
                parser.error(str(error))
            emit_json({"contradiction": result})
            return 0

        migration = migrate_legacy_chroma(collection)
        workspace_migration = migrate_legacy_workspace_storage()
        provenance = backfill_existing_provenance()
        if arguments.storage_command == "migrate":
            emit_json({"storage": {
                "migration": migration,
                "workspace_migration": workspace_migration,
                "provenance": provenance,
            }})
        elif arguments.storage_command == "rebuild-index":
            from memory.embedder import embed
            result = rebuild_guidance_index(collection, embed)
            emit_json({"storage": {
                "migration": migration,
                "workspace_migration": workspace_migration,
                "provenance": provenance,
                "index": result,
            }})
        elif arguments.storage_command == "export":
            emit_json({"storage": {"export": export_snapshot(arguments.output)}})
        elif arguments.storage_command == "backup":
            emit_json({"storage": {"backup": create_backup(arguments.output)}})
        else:
            emit_json({"storage": {
                "migration": migration,
                "workspace_migration": workspace_migration,
                "provenance": provenance,
                "restore": restore_snapshot(arguments.input),
            }})
        return 0

    try:
        request = load_json_request(arguments.input)
        environment = request.get("environment")
        if environment is not None and not isinstance(environment, dict):
            raise ValueError("Request field 'environment' must be an object when provided.")

        if arguments.command == "intervene":
            options = dict(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
                token_budget=request.get("token_budget", 450),
            )
            if environment is not None:
                options["environment"] = environment
            result = intervene_cognition(**options)
        elif arguments.command == "autopilot":
            result = autopilot_event_cognition(
                event=require_text(request, "event"),
                task_id=require_text(request, "task_id"),
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
                environment=environment,
                context=request.get("context"),
                action=request.get("action"),
                outcome=request.get("outcome"),
                token_budget=request.get("token_budget", 450),
                host=request.get("host"),
            )
        elif arguments.command == "autopilot-control":
            result = autopilot_control_cognition(
                action=require_text(request, "action"),
                agent_id=request.get("agent_id", "automation"),
                task_id=request.get("task_id"),
            )
        elif arguments.command == "dream":
            result = dream_cognition(
                action=request.get("action", "run"),
                agent_id=request.get("agent_id", "automation"),
                environment=environment,
                max_candidates=request.get("max_candidates", 5),
                candidate_id=request.get("candidate_id"),
                checks=request.get("checks"),
                auto_promote=bool(request.get("auto_promote", True)),
            )
        elif arguments.command == "contract":
            contract = request.get("contract")
            observations = request.get("observations")
            result = cognition_contract_cognition(contract, observations)
        elif arguments.command == "host-certify":
            result = certify_host_cognition(
                host=require_text(request, "host"),
                events=request.get("events"),
                strict=bool(request.get("strict", False)),
            )
        elif arguments.command == "token-ledger":
            result = token_ledger_cognition(
                agent_id=request.get("agent_id", "automation"),
                task_id=request.get("task_id"),
            )
        elif arguments.command == "skill-compile":
            definition = request.get("definition")
            if not isinstance(definition, dict):
                raise ValueError("Request field 'definition' must be an object.")
            result = compile_skill_cognition(
                definition,
                require_text(request, "problem"),
                environment=environment,
            )
        elif arguments.command == "skill-compose":
            result = compose_skills_cognition(request.get("definitions"))
        elif arguments.command == "skill-evolve":
            definition, changes = request.get("definition"), request.get("changes")
            if not isinstance(definition, dict) or not isinstance(changes, dict):
                raise ValueError("Request fields 'definition' and 'changes' must be objects.")
            result = evolve_skill_cognition(definition, changes, project_id=request.get("project_id"))
        elif arguments.command == "skill-credit":
            result = skill_credit_cognition(
                skill_id=require_text(request, "skill_id"),
                outcome=require_text(request, "outcome"),
                influence=require_text(request, "influence"),
                agent_id=request.get("agent_id", "automation"),
                changed_steps=request.get("changed_steps"),
                warning=request.get("warning"),
            )
        elif arguments.command == "utility-feedback":
            result = utility_feedback_cognition(
                intervention_id=require_text(request, "intervention_id"),
                rating=require_text(request, "rating"),
                agent_id=request.get("agent_id", "automation"),
                reason=request.get("reason"),
                action=request.get("action"),
                outcome=request.get("outcome"),
                mute=bool(request.get("mute", False)),
                applicability_correction=request.get("applicability_correction"),
            )
        elif arguments.command == "utility-summary":
            result = utility_feedback_summary_cognition(
                memory_id=request.get("memory_id"),
                agent_id=request.get("agent_id", "automation"),
                environment=environment,
            )
        elif arguments.command == "frontier":
            result = failure_frontier_cognition(
                action=request.get("action", "match"),
                problem=request.get("problem"),
                trigger=request.get("trigger"),
                risk=request.get("risk"),
                warning=request.get("warning"),
                verification=request.get("verification"),
                owner=request.get("owner", request.get("agent_id", "automation")),
                environment=environment,
                counterexamples=request.get("counterexamples"),
                source_memory_ids=request.get("source_memory_ids"),
                frontier_id=request.get("frontier_id"),
                status=request.get("status"),
                outcome=request.get("outcome"),
                reason=request.get("reason"),
                limit=request.get("limit", 5),
            )
        elif arguments.command == "branch":
            result = cognitive_branch_cognition(
                action=request.get("action", "list"),
                branch_id=request.get("branch_id"),
                target_branch_id=request.get("target_branch_id"),
                name=request.get("name"),
                owner=request.get("owner", request.get("agent_id", "automation")),
                project_id=request.get("project_id"),
                environment=environment,
                base_environment=request.get("base_environment"),
                base_ref=request.get("base_ref"),
                kind=request.get("kind"),
                key=request.get("key"),
                before=request.get("before"),
                after=request.get("after"),
                memory_ids=request.get("memory_ids"),
                obligation_id=request.get("obligation_id"),
                obligation_name=request.get("obligation_name"),
                obligation_kind=request.get("obligation_kind", "test"),
                command=request.get("command"),
                passed=request.get("passed"),
                evidence=request.get("evidence"),
                apply=bool(request.get("apply", False)),
                reason=request.get("reason"),
                status=request.get("status"),
            )
        elif arguments.command == "retrieval-debug":
            result = retrieval_debug_cognition(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
                environment=environment,
                utility_threshold=request.get("utility_threshold"),
            )
        elif arguments.command == "checkpoint":
            update = request.get("update")
            if not isinstance(update, dict):
                raise ValueError("Request field 'update' must be an object.")
            result = checkpoint_cognition(
                task_id=require_text(request, "task_id"),
                update=update,
                agent_id=request.get("agent_id", "automation"),
                prediction_result=request.get("prediction_result"),
            )
        elif arguments.command == "task-state":
            result = task_state_cognition(
                task_id=require_text(request, "task_id"),
                agent_id=request.get("agent_id", "automation"),
            )
        elif arguments.command == "project-update":
            update = request.get("update")
            if not isinstance(update, dict):
                raise ValueError("Request field 'update' must be an object.")
            result = project_update_cognition(
                project_id=require_text(request, "project_id"),
                update=update,
                agent_id=request.get("agent_id", "automation"),
                environment=environment,
            )
        elif arguments.command == "project-resurrect":
            result = project_resurrect_cognition(
                project_id=require_text(request, "project_id"),
                agent_id=request.get("agent_id", "automation"),
                environment=environment,
                token_budget=request.get("token_budget", 600),
            )
        elif arguments.command == "project-handoff":
            result = project_handoff_cognition(
                project_id=require_text(request, "project_id"),
                agent_id=request.get("agent_id", "automation"),
                environment=environment,
            )
        elif arguments.command == "project-accept":
            capsule = request.get("capsule")
            if not isinstance(capsule, dict):
                raise ValueError("Request field 'capsule' must be an object.")
            result = project_accept_cognition(
                capsule=capsule,
                agent_id=request.get("agent_id", "automation"),
                environment=environment,
            )
        elif arguments.command == "start":
            options = dict(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
            )
            if environment is not None:
                options["environment"] = environment
            result = start_cognition(**options)
        elif arguments.command == "plan-history":
            result = plan_history_cognition(
                plan_id=require_text(request, "plan_id"),
                agent_id=request.get("agent_id", "automation"),
            )
        elif arguments.command == "skill-health":
            result = skill_health_cognition(
                skill_id=require_text(request, "skill_id"),
                agent_id=request.get("agent_id", "automation"),
            )
        elif arguments.command == "evaluate":
            runs = request.get("runs")
            result = evaluate_cognition(runs)
        elif arguments.command == "policy":
            result = policy_cognition(request.get("action", "status"), request)
        elif arguments.command == "capsule":
            result = capsule_cognition(request.get("action", "inspect"), request)
        elif arguments.command == "replay":
            result = replay_cognition(request.get("action", "compare"), request)
        elif arguments.command == "prepare":
            options = dict(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
                include_skills=bool(request.get("include_skills", True)),
                detail_level=request.get("detail_level", "brief"),
            )
            if environment is not None:
                options["environment"] = environment
            result = prepare_cognition(**options)
        elif arguments.command == "plan":
            options = dict(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
            )
            if environment is not None:
                options["environment"] = environment
            result = plan_cognition(**options)
        elif arguments.command == "skill":
            contract_fields = (
                "purpose", "preconditions", "decision_points", "expected_observations",
                "failure_handling", "rollback", "applicability_limits", "state_mutations",
                "resources",
            )
            result = promote_skill_cognition(
                name=require_text(request, "name"),
                when_to_use=require_text(request, "when_to_use"),
                inputs=request.get("inputs"),
                steps=request.get("steps"),
                verification=request.get("verification"),
                supporting_experience_ids=request.get("supporting_experience_ids"),
                supporting_principle_ids=request.get("supporting_principle_ids"),
                agent_id=request.get("agent_id", "automation"),
                human_approved=bool(request.get("human_approved", False)),
                **{field: request.get(field) for field in contract_fields if field in request},
            )
        else:
            files = request.get("files")
            if not isinstance(files, list):
                raise ValueError("Request field 'files' must be a list.")

            evidence = request.get("evidence")
            if not isinstance(evidence, dict):
                raise ValueError("Request field 'evidence' must be an object with verification checks.")

            principles = request.get("principles")
            if principles is not None and not isinstance(principles, list):
                raise ValueError("Request field 'principles' must be a list when provided.")

            outcome = {
                "task": require_text(request, "task"),
                "files": files,
                "summary": require_text(request, "summary"),
                "solution": require_text(request, "solution"),
                "reflection": request.get("reflection"),
                "principles": principles,
                "evidence": evidence,
            }
            if environment is not None:
                outcome["environment"] = environment
            if arguments.command == "verify":
                result = verify_cognition(**outcome)
            else:
                result = record_cognition(
                    **outcome,
                    plan_id=request.get("plan_id"),
                    applied_skill_id=request.get("applied_skill_id"),
                    agent_id=request.get("agent_id", "automation")
                )
    except ValueError as error:
        emit_json({
            "error": {
                "code": "invalid_request",
                "message": str(error)
            }
        })
        return 2

    emit_json(result)
    return 0
