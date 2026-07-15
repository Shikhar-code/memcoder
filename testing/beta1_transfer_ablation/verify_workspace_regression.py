"""Hold-out regression check: do not show this to the agent during stage 2."""

from workspace_validation import validate_workspace


def test_blank_workspace_name_is_rejected_cleanly():
    try:
        validate_workspace({"workspace_name": "   "})
    except ValueError as error:
        assert str(error) == "workspace_name is required"
        return

    raise AssertionError(
        "Expected ValueError('workspace_name is required') for a blank workspace_name."
    )


test_blank_workspace_name_is_rejected_cleanly()

print("PASS: workspace hold-out regression")
