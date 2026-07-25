from api_key import validate_request


try:
    validate_request({})
except ValueError as error:
    assert str(error) == "api_key is required"
else:
    raise AssertionError("Expected missing api_key validation failure")

assert validate_request({"api_key": " key-1 "})["api_key"] == "key-1"
print("PASS: public api key validation")
