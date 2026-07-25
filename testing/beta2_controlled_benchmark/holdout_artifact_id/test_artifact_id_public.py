from artifact_id import register_artifact


try:
    register_artifact({})
except ValueError as error:
    assert str(error) == "artifact_id is required"
else:
    raise AssertionError("Expected missing artifact_id validation failure")

assert register_artifact({"artifact_id": " asset-9 "})["artifact_id"] == "asset-9"
print("PASS: public artifact id validation")
