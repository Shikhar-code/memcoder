def validate_deployment_config(config):
    if "deployment_name" not in config:
        raise ValueError("deployment_name is required")
    deployment_name = config["deployment_name"].strip()
    region = config.get("region", "default").strip()

    return {
        "deployment_name": deployment_name,
        "region": region
    }
