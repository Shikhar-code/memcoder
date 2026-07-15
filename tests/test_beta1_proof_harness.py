import importlib.util
from pathlib import Path


script_path = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "verify_beta1_proof.py"
)

spec = importlib.util.spec_from_file_location(
    "verify_beta1_proof",
    script_path
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

counts = module.count_by_type([
    {"type": "experience"},
    {"type": "experience"},
    {"type": "reflection"}
])

assert counts["experience"] == 2
assert counts["reflection"] == 1
assert module.validation_failures(counts, 1, 1) == []
assert module.validation_failures(counts, 3, 1)
assert module.validation_failures(counts, 1, 2)

print("PASS: Beta-1 proof harness")
