from tenant_id import select_tenant


try:
    select_tenant({})
except ValueError as error:
    assert str(error) == "tenant_id is required"
else:
    raise AssertionError("Expected missing tenant_id validation failure")

assert select_tenant({"tenant_id": " tenant-a "})["tenant_id"] == "tenant-a"
print("PASS: public tenant id validation")
