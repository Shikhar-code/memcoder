from profile_validation import validate_profile


def expect_required_error(profile):
    try:
        validate_profile(profile)
    except ValueError as error:
        assert str(error) == "profile_name is required"
        return

    raise AssertionError("Expected ValueError('profile_name is required').")


expect_required_error({"region": "us-east"})
expect_required_error({"profile_name": "   "})

print("PASS: profile validation")
