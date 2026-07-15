"""Hold-out counterpart for the no-memory workspace control task."""

from workspace_control_validation import validate_workspace_control


def test_blank_workspace_name_is_rejected_cleanly():
    try:
        validate_workspace_control({"workspace_name": "   "})
    except ValueError as error:
        assert str(error) == "workspace_name is required"
        return

    raise AssertionError(
        "Expected ValueError('workspace_name is required') for a blank workspace_name."
    )


test_blank_workspace_name_is_rejected_cleanly()

print("PASS: workspace control hold-out regression")
