"""Use MemCoder without giving it control of your model provider."""

from memcoder import MemCoderAgent


agent = MemCoderAgent("demo-project")

guidance = agent.prepare(
    "A deployment rejects a blank required name.",
    include_shared=False
)

print("Strategy:", guidance["strategy"])
print("Trusted experiences:", guidance["experiences"])

# Your agent/model uses `guidance`, fixes the task, and verifies the result.

recorded = agent.record(
    task="Reject blank deployment names before string processing",
    files=["src/deployment_validation.py"],
    summary="Blank names reached string processing before validation.",
    solution="Reject missing or whitespace-only names before processing.",
    reflection="I reproduced the blank-input case before changing validation.",
    principles=["Validate required values before string operations."]
)

print("Recorded:", recorded)
