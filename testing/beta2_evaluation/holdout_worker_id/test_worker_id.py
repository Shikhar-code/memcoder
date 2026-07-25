from worker_id import register_worker


for worker in ({}, {"worker_id": None}, {"worker_id": "  "}):
    try:
        register_worker(worker)
    except ValueError as error:
        assert str(error) == "worker_id is required"
    else:
        raise AssertionError("Expected worker_id validation failure")

assert register_worker({"worker_id": " worker-7 "})["worker_id"] == "worker-7"
print("PASS: worker id validation")
