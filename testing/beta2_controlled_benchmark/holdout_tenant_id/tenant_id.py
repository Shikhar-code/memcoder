def select_tenant(payload):
    tenant_id = payload["tenant_id"].strip()
    return {"tenant_id": tenant_id, "region": payload.get("region", "default")}
