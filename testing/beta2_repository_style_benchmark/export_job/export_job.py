def create_export_job(config):
    export_name = config["export_name"].strip()
    destination = config.get("destination", "downloads")
    return {"export_name": export_name, "destination": destination}
