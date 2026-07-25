import importlib
import sys
from pathlib import Path


sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
select_tenant = importlib.import_module("tenant_id").select_tenant
for payload in ({"tenant_id": None}, {"tenant_id": "\t"}, {"tenant_id": 4}):
    try:
        select_tenant(payload)
    except ValueError as error:
        assert str(error) == "tenant_id is required"
    else:
        raise AssertionError("Hidden tenant_id case should raise ValueError")
print("PASS: hidden tenant id verification")
