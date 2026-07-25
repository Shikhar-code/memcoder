"""Small, dependency-free setup commands for MemCoder users."""

import argparse
import json
import sys
from pathlib import Path

from api.cognition import (
    evaluate_cognition,
    plan_history_cognition,
    plan_cognition,
    prepare_cognition,
    promote_skill_cognition,
    record_cognition,
    skill_health_cognition,
    start_cognition,
    verify_cognition,
)


def default_agy_config_path():
    """Return AGY's per-user MCP configuration path."""
    return Path.home() / ".gemini" / "antigravity" / "mcp_config.json"


def configure_agy(config_path, python_executable):
    """Add or update MemCoder without disturbing other MCP servers."""
    config_path = Path(config_path)
    config = {}

    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Cannot update invalid JSON configuration: {config_path}"
            ) from error

    if not isinstance(config, dict):
        raise ValueError("AGY MCP configuration must contain a JSON object.")

    servers = config.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError("AGY MCP configuration field 'mcpServers' must be an object.")

    servers["memcoder"] = {
        "command": str(Path(python_executable).resolve()),
        "args": ["-m", "adapters.mcp.server"]
    }

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return config_path


def load_json_request(input_path):
    """Load one JSON-object request from a file or standard input."""
    try:
        raw = sys.stdin.read() if str(input_path) == "-" else Path(input_path).read_text(
            encoding="utf-8"
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

    for command, help_text in (
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

    try:
        request = load_json_request(arguments.input)

        if arguments.command == "start":
            result = start_cognition(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
            )
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
        elif arguments.command == "prepare":
            result = prepare_cognition(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
                include_skills=bool(request.get("include_skills", True)),
                detail_level=request.get("detail_level", "brief"),
            )
        elif arguments.command == "plan":
            result = plan_cognition(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True)),
            )
        elif arguments.command == "skill":
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
