def validate_service(config):
    service_name = config["service_name"].strip()
    return {"service_name": service_name, "region": config.get("region", "default")}
