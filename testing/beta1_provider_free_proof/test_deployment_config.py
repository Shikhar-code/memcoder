from deployment_config import validate_deployment_config


def test_missing_deployment_name_is_rejected_cleanly():
    try:
        validate_deployment_config({"region": "us-east"})
    except ValueError as error:
        assert str(error) == "deployment_name is required"
        return

    raise AssertionError(
        "Expected ValueError('deployment_name is required') for a missing deployment_name."
    )


test_missing_deployment_name_is_rejected_cleanly()

print("PASS: deployment config validation")
