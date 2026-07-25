import importlib
import sys
from pathlib import Path


sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
register_artifact = importlib.import_module("artifact_id").register_artifact
for artifact in ({"artifact_id": None}, {"artifact_id": "   "}, {"artifact_id": {}}):
    try:
        register_artifact(artifact)
    except ValueError as error:
        assert str(error) == "artifact_id is required"
    else:
        raise AssertionError("Hidden artifact_id case should raise ValueError")
print("PASS: hidden artifact id verification")
