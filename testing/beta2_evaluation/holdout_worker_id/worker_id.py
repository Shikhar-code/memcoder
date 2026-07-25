def register_worker(worker):
    worker_id = worker["worker_id"].strip()
    return {"worker_id": worker_id, "queue": worker.get("queue", "default")}
