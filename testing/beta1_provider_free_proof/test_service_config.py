from service_config import validate_service_config


def test_missing_service_name_is_rejected_cleanly():
    try:
        validate_service_config({"region": "us-east"})
    except ValueError as error:
        assert str(error) == "service_name is required"
        return

    raise AssertionError(
        "Expected ValueError('service_name is required') for a missing service_name."
    )


test_missing_service_name_is_rejected_cleanly()

print("PASS: service config validation")
