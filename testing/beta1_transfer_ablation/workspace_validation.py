def validate_workspace(workspace):
    workspace_name = workspace.get("workspace_name")
    if not workspace_name or not isinstance(workspace_name, str) or not workspace_name.strip():
        raise ValueError("workspace_name is required")
    workspace_name = workspace_name.strip()
    region = workspace.get("region", "default").strip()

    return {
        "workspace_name": workspace_name,
        "region": region
    }
