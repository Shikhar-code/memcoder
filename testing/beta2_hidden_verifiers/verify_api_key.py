import importlib
import sys
from pathlib import Path


sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
validate_request = importlib.import_module("api_key").validate_request
for request in ({"api_key": None}, {"api_key": "  "}, {"api_key": 17}):
    try:
        validate_request(request)
    except ValueError as error:
        assert str(error) == "api_key is required"
    else:
        raise AssertionError("Hidden api_key case should raise ValueError")
print("PASS: hidden api key verification")
