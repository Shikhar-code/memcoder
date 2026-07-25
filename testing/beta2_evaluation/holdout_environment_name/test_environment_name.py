from environment_name import parse_environment


for settings in ({}, {"environment": None}, {"environment": "   "}):
    try:
        parse_environment(settings)
    except ValueError as error:
        assert str(error) == "environment is required"
    else:
        raise AssertionError("Expected environment validation failure")

assert parse_environment({"environment": " staging "})["environment"] == "staging"
print("PASS: environment name validation")
