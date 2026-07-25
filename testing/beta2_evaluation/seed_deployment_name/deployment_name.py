def validate_deployment(config):
    deployment_name = config["deployment_name"].strip()
    return {"deployment_name": deployment_name, "region": config.get("region", "default")}
