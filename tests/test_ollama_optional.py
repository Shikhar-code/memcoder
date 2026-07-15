"""Regression checks for the provider-free base installation."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {"build", ".ipynb_checkpoints", ".git", ".venv"}


def has_direct_ollama_import(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return any(
        isinstance(node, ast.Import)
        and any(alias.name == "ollama" for alias in node.names)
        for node in ast.walk(tree)
    )


source_files = [
    path
    for path in ROOT.rglob("*.py")
    if not any(part in EXCLUDED_PARTS for part in path.parts)
]

direct_imports = [
    path.relative_to(ROOT)
    for path in source_files
    if path.name != "optional_ollama.py" and has_direct_ollama_import(path)
]

assert not direct_imports, (
    "Base MemCoder code must not directly import Ollama: "
    f"{direct_imports}"
)

pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
main_dependencies = pyproject.split("[project.optional-dependencies]", 1)[0]
assert '"ollama"' not in main_dependencies

print("PASS: Ollama is optional")
