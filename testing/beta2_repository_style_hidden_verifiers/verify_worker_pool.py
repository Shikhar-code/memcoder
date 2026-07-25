import sys
from pathlib import Path


sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from worker_pool import register_worker


for value in (None, "   ", 7, ("image-worker",)):
    try:
        register_worker({"worker_name": value})
    except ValueError as error:
        assert str(error) == "worker_name is required"
    else:
        raise AssertionError("Hidden worker_name case should raise ValueError")

print("PASS: hidden worker pool verification")
