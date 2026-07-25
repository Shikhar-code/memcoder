from profile_email import validate_profile


for profile in ({}, {"email": None}, {"email": "\n"}):
    try:
        validate_profile(profile)
    except ValueError as error:
        assert str(error) == "email is required"
    else:
        raise AssertionError("Expected email validation failure")

assert validate_profile({"email": " student@example.com "})["email"] == "student@example.com"
print("PASS: profile email validation")
