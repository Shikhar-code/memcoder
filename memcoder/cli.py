"""Small, dependency-free setup commands for MemCoder users."""

import argparse
import json
import sys
from pathlib import Path

from api.cognition import prepare_cognition, record_cognition


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
            ("prepare", "Retrieve provider-free cognition from a JSON request."),
            ("record", "Store a verified outcome from a JSON request.")):
        subcommand = subcommands.add_parser(command, help=help_text)
        subcommand.add_argument(
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

        if arguments.command == "prepare":
            result = prepare_cognition(
                problem=require_text(request, "problem"),
                agent_id=request.get("agent_id", "automation"),
                include_shared=bool(request.get("include_shared", True))
            )
        else:
            if request.get("verified") is not True:
                raise ValueError(
                    "Record requests require 'verified': true after host verification."
                )

            files = request.get("files")
            if not isinstance(files, list):
                raise ValueError("Request field 'files' must be a list.")

            principles = request.get("principles")
            if principles is not None and not isinstance(principles, list):
                raise ValueError("Request field 'principles' must be a list when provided.")

            result = record_cognition(
                task=require_text(request, "task"),
                files=files,
                summary=require_text(request, "summary"),
                solution=require_text(request, "solution"),
                reflection=request.get("reflection"),
                principles=principles,
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
