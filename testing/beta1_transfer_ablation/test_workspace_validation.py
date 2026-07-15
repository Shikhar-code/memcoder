from workspace_validation import validate_workspace


def test_missing_workspace_name_is_rejected_cleanly():
    try:
        validate_workspace({"region": "us-east"})
    except ValueError as error:
        assert str(error) == "workspace_name is required"
        return

    raise AssertionError(
        "Expected ValueError('workspace_name is required') for a missing workspace_name."
    )


test_missing_workspace_name_is_rejected_cleanly()

print("PASS: workspace validation")
