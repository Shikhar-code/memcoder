def configure_channel(config):
    channel_name = config["channel_name"].strip()
    return {"channel_name": channel_name, "enabled": bool(config.get("enabled", True))}
