import sys
from pathlib import Path


sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from export_job import create_export_job


for value in (None, "   ", 7, {"weekly": True}):
    try:
        create_export_job({"export_name": value})
    except ValueError as error:
        assert str(error) == "export_name is required"
    else:
        raise AssertionError("Hidden export_name case should raise ValueError")

print("PASS: hidden export job verification")
