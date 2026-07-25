from batch_job_id import queue_jobs


for jobs in ([{}], [{"job_id": None}], [{"job_id": "  "}]):
    try:
        queue_jobs(jobs)
    except ValueError as error:
        assert str(error) == "job_id is required"
    else:
        raise AssertionError("Expected job_id validation failure")

assert queue_jobs([{"job_id": " job-1 "}, {"job_id": "job-2"}]) == ["job-1", "job-2"]
print("PASS: batch job id validation")
