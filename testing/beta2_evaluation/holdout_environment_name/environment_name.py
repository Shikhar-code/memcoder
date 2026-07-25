def parse_environment(settings):
    environment = settings["environment"].strip()
    return {"environment": environment, "debug": bool(settings.get("debug", False))}
