from service_name import validate_service


def expect_required(config):
    try:
        validate_service(config)
    except ValueError as error:
        assert str(error) == "service_name is required"
    else:
        raise AssertionError("Expected ValueError for missing service_name")


expect_required({})
expect_required({"service_name": "   "})
assert validate_service({"service_name": " billing "})["service_name"] == "billing"
print("PASS: service name validation")
