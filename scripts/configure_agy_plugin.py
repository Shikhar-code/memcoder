"""Create the local MCP config AGY needs for this checkout.

Run this from the Python environment where ``python -m pip install .`` was
executed. The generated config is intentionally ignored by Git because it
contains a machine-specific Python path.
"""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "mcp_config.json"

config = {
    "mcpServers": {
        "memcoder": {
            "command": str(Path(sys.executable).resolve()),
            "args": ["-m", "adapters.mcp.server"]
        }
    }
}

CONFIG_PATH.write_text(
    json.dumps(config, indent=2) + "\n",
    encoding="utf-8"
)

print(f"Created {CONFIG_PATH}")
print(f"Next: agy plugin install {ROOT}")
print("Then: agy plugin enable memcoder")
