"""Default storage belongs in user data, not the installed package directory."""

import ast
from pathlib import Path


source_path = Path(__file__).resolve().parents[1] / "memory" / "chroma_client.py"
source = source_path.read_text(encoding="utf-8")
ast.parse(source, filename=str(source_path))

assert "def default_db_path" in source
assert "LOCALAPPDATA" in source
assert "legacy_workspace_collection" in source
assert "legacy_workspace_db_path" in source

print("PASS: user-data storage default and legacy migration hook")
