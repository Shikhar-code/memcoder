"""Bind the local Codex plugin to the Python running this script."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "codex-marketplace" / "plugins" / "memcoder" / ".mcp.json"


def build_config():
    return {
        "mcpServers": {
            "memcoder": {
                "command": sys.executable,
                "args": ["-m", "adapters.mcp.server"],
                "cwd": str(ROOT),
                "startup_timeout_sec": 60,
                "tool_timeout_sec": 120,
            }
        }
    }


def main():
    CONFIG_PATH.write_text(
        json.dumps(build_config(), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Configured {CONFIG_PATH}")
    print(f"Python: {sys.executable}")


if __name__ == "__main__":
    main()
