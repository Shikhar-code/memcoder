"""Small, dependency-free setup commands for MemCoder users."""

import argparse
import json
import sys
from pathlib import Path

from api.cognition import prepare_cognition, record_cognition
from memory.knowledge import (
    configure_knowledge,
    knowledge_status,
    load_knowledge_config,
    sync_knowledge,
)
from memory.assets import search_assets, write_asset_catalog


# The CLI is often invoked by another automation process on Windows.  Its
# output is JSON and may contain Unicode copied from Markdown knowledge, so it
# must not inherit a legacy CP1252 console encoding and fail while emitting a
# valid result.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


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

    subcommands.choices["prepare"].add_argument(
        "--config",
        help="Optional project knowledge configuration file."
    )

    knowledge_sync = subcommands.add_parser(
        "knowledge",
        help="Manage the separate, read-only Markdown knowledge index."
    )
    knowledge_subcommands = knowledge_sync.add_subparsers(
        dest="knowledge_command",
        required=True,
    )
    knowledge_sync_command = knowledge_subcommands.add_parser(
        "sync",
        help="Incrementally index Markdown knowledge from an approved directory."
    )
    sync_source = knowledge_sync_command.add_mutually_exclusive_group()
    sync_source.add_argument(
        "--source",
        help="Directory containing Markdown knowledge files."
    )
    sync_source.add_argument(
        "--config",
        help="Project knowledge configuration file."
    )
    knowledge_status_command = knowledge_subcommands.add_parser(
        "status",
        help="Show the current local knowledge-index health and scope."
    )
    knowledge_status_command.add_argument(
        "--source",
        help="Optionally report status for one configured Markdown source."
    )
    knowledge_status_command.add_argument(
        "--config",
        help="Project knowledge configuration file."
    )
    knowledge_configure_command = knowledge_subcommands.add_parser(
        "configure",
        help="Write a project-local source and agent identity contract."
    )
    knowledge_configure_command.add_argument(
        "--source",
        required=True,
        help="Directory containing Markdown knowledge files."
    )

    assets_command = subcommands.add_parser(
        "assets",
        help="Build and search a separate approved visual-asset catalog."
    )
    assets_subcommands = assets_command.add_subparsers(
        dest="assets_command",
        required=True,
    )
    assets_catalog_command = assets_subcommands.add_parser(
        "catalog",
        help="Create deterministic metadata for approved image, SVG, and video assets."
    )
    assets_catalog_command.add_argument("--source", required=True)
    assets_catalog_command.add_argument("--output", required=True)
    assets_catalog_command.add_argument(
        "--metadata",
        help="Optional JSON overlay keyed by relative asset path for curated concepts and visual types.",
    )
    assets_catalog_command.add_argument(
        "--subject",
        help="Optionally catalog one normalized subject, such as economics or physics.",
    )
    assets_search_command = assets_subcommands.add_parser(
        "search",
        help="Search one generated asset catalog without loading asset binaries."
    )
    assets_search_command.add_argument("--catalog", required=True)
    assets_search_command.add_argument("--query", required=True)
    assets_search_command.add_argument("--subject")
    assets_search_command.add_argument("--limit", type=int, default=8)
    knowledge_configure_command.add_argument(
        "--agent-id",
        required=True,
        help="Stable MemCoder owner label for this automation project."
    )
    knowledge_configure_command.add_argument(
        "--config",
        help="Destination configuration file (default: .memcoder/knowledge.json)."
    )
    knowledge_configure_command.add_argument(
        "--include-shared",
        action="store_true",
        help="Allow intentionally shared learned memories for this project."
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

    if arguments.command == "knowledge":
        try:
            if arguments.knowledge_command == "sync":
                config = (
                    load_knowledge_config(arguments.config)
                    if arguments.config else None
                )
                source = arguments.source or (config or {}).get("source_root")
                if not source:
                    raise ValueError("Knowledge sync requires --source or --config.")
                result = sync_knowledge(source)
            elif arguments.knowledge_command == "configure":
                result = configure_knowledge(
                    source_root=arguments.source,
                    agent_id=arguments.agent_id,
                    config_path=arguments.config,
                    include_shared=arguments.include_shared,
                )
            else:
                config = (
                    load_knowledge_config(arguments.config)
                    if arguments.config else None
                )
                result = knowledge_status(
                    arguments.source or (config or {}).get("source_root")
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

    if arguments.command == "assets":
        try:
            if arguments.assets_command == "catalog":
                result = write_asset_catalog(
                    arguments.source,
                    arguments.output,
                    subject=arguments.subject,
                    metadata_path=arguments.metadata,
                )
            else:
                result = search_assets(
                    arguments.catalog,
                    arguments.query,
                    subject=arguments.subject,
                    limit=arguments.limit,
                )
        except ValueError as error:
            emit_json({"error": {"code": "invalid_request", "message": str(error)}})
            return 2
        emit_json(result)
        return 0

    try:
        request = load_json_request(arguments.input)

        if arguments.command == "prepare":
            config = (
                load_knowledge_config(arguments.config)
                if arguments.config else {}
            )
            prepare_arguments = {
                "problem": require_text(request, "problem"),
                "agent_id": request.get("agent_id", config.get("agent_id", "automation")),
                "include_shared": bool(
                    request.get("include_shared", config.get("include_shared", True))
                ),
                "include_knowledge": bool(
                    request.get("include_knowledge", config.get("include_knowledge", True))
                ),
            }
            for field in ("subject", "category"):
                if field in request:
                    prepare_arguments[field] = require_text(request, field)
            result = prepare_cognition(**prepare_arguments)
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
