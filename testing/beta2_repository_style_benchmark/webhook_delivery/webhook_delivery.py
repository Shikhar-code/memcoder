def build_delivery(payload):
    endpoint_name = payload["endpoint_name"].strip()
    timeout_seconds = payload.get("timeout_seconds", 30)
    return {"endpoint_name": endpoint_name, "timeout_seconds": timeout_seconds}
