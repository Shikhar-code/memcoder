def register_artifact(artifact):
    artifact_id = artifact["artifact_id"].strip()
    return {"artifact_id": artifact_id, "kind": artifact.get("kind", "generic")}
