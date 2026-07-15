import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)

from memory.relevance import (
    filter_trusted_memories,
    memory_confidence
)


query = "queue_jobs receives a job without its required job_id field"

cross_task_memory = {
    "task": "create_project raises ValueError when name is required",
    "summary": "A required name field was accessed before validation.",
    "solution": "Validate required fields before accessing them.",
    "files": ["request_validation.py"],
    "score": 0.756
}

irrelevant_midband_memory = {
    "task": "Update a color theme",
    "summary": "The dashboard palette needed a visual refresh.",
    "solution": "Change the CSS color variables.",
    "files": ["theme.css"],
    "score": 0.700
}

unrelated_memory = {
    "task": "Repair a database connection",
    "summary": "The service could not connect to PostgreSQL.",
    "solution": "Check database credentials and network settings.",
    "files": ["database.py"],
    "score": 0.900
}

assert memory_confidence(cross_task_memory) == 0.622

trusted = filter_trusted_memories(
    [
        cross_task_memory,
        irrelevant_midband_memory,
        unrelated_memory
    ],
    query=query
)

assert [memory["task"] for memory in trusted] == [
    cross_task_memory["task"]
]

print("PASS: retrieval calibration")
