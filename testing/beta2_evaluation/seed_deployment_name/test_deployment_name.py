from deployment_name import validate_deployment


def expect_required(config):
    try:
        validate_deployment(config)
    except ValueError as error:
        assert str(error) == "deployment_name is required"
    else:
        raise AssertionError("Expected ValueError for missing deployment_name")


expect_required({})
expect_required({"deployment_name": "\t"})
assert validate_deployment({"deployment_name": " prod "})["deployment_name"] == "prod"
print("PASS: deployment name validation")
