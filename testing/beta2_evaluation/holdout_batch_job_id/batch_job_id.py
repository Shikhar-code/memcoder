def queue_jobs(jobs):
    queued = []
    for job in jobs:
        job_id = job["job_id"].strip()
        queued.append(job_id)
    return queued
