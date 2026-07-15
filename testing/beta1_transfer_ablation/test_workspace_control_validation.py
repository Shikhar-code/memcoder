from workspace_control_validation import validate_workspace_control


def test_missing_workspace_name_is_rejected_cleanly():
    try:
        validate_workspace_control({"region": "us-east"})
    except ValueError as error:
        assert str(error) == "workspace_name is required"
        return

    raise AssertionError(
        "Expected ValueError('workspace_name is required') for a missing workspace_name."
    )


test_missing_workspace_name_is_rejected_cleanly()

print("PASS: workspace control validation")
