from export_job import create_export_job


try:
    create_export_job({})
except ValueError as error:
    assert str(error) == "export_name is required"
else:
    raise AssertionError("Missing export_name should raise ValueError")

assert create_export_job({"export_name": " weekly-summary "}) == {
    "export_name": "weekly-summary",
    "destination": "downloads",
}

print("PASS: public export job validation")
