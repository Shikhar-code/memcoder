def validate_workspace_control(workspace):
    if "workspace_name" not in workspace or workspace["workspace_name"] is None:
        raise ValueError("workspace_name is required")
    workspace_name = workspace["workspace_name"].strip()
    region = workspace.get("region", "default").strip()

    return {
        "workspace_name": workspace_name,
        "region": region
    }
