"""AGY setup must use the installing interpreter and preserve other servers."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.append(str(Path(__file__).resolve().parents[1]))

from memcoder.cli import configure_agy


with TemporaryDirectory() as temporary_directory:
    config_path = Path(temporary_directory) / "antigravity" / "mcp_config.json"
    config_path.parent.mkdir()
    config_path.write_text(
        json.dumps({"mcpServers": {"other": {"command": "other-server"}}}),
        encoding="utf-8"
    )

    written_path = configure_agy(config_path, sys.executable)
    config = json.loads(written_path.read_text(encoding="utf-8"))

    assert config["mcpServers"]["other"] == {"command": "other-server"}
    assert config["mcpServers"]["memcoder"] == {
        "command": str(Path(sys.executable).resolve()),
        "args": ["-m", "adapters.mcp.server"]
    }

print("PASS: AGY setup CLI")
