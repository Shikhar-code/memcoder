def register_worker(worker):
    worker_name = worker["worker_name"].strip()
    queue = worker.get("queue", "default")
    return {"worker_name": worker_name, "queue": queue}
