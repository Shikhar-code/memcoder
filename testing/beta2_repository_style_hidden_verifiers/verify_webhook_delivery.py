import sys
from pathlib import Path


sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from webhook_delivery import build_delivery


for value in (None, "   ", 7, ["billing-events"]):
    try:
        build_delivery({"endpoint_name": value})
    except ValueError as error:
        assert str(error) == "endpoint_name is required"
    else:
        raise AssertionError("Hidden endpoint_name case should raise ValueError")

print("PASS: hidden webhook delivery verification")
