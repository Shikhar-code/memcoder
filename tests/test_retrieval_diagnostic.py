import importlib.util
from pathlib import Path


script_path = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "diagnose_retrieval.py"
)

spec = importlib.util.spec_from_file_location(
    "diagnose_retrieval",
    script_path
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

formatted = module.format_candidate({
    "task": "Validate a required field",
    "score": 0.25
})

assert "distance=0.250" in formatted
assert "confidence=0.88" in formatted
assert "task=Validate a required field" in formatted

print("PASS: retrieval diagnostic")
