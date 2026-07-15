def validate_service_config(config):
    if "service_name" not in config:
        raise ValueError("service_name is required")
    service_name = config["service_name"].strip()
    region = config.get("region", "default").strip()

    return {
        "service_name": service_name,
        "region": region
    }
