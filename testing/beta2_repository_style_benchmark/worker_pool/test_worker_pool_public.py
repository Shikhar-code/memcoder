from worker_pool import register_worker


try:
    register_worker({})
except ValueError as error:
    assert str(error) == "worker_name is required"
else:
    raise AssertionError("Missing worker_name should raise ValueError")

assert register_worker({"worker_name": " image-worker ", "queue": "media"}) == {
    "worker_name": "image-worker",
    "queue": "media",
}

print("PASS: public worker pool validation")
