import os
import tempfile

from memory.utility import (
    apply_utility_policy,
    build_receipt,
    record_feedback,
    save_receipt,
)


def candidate(task, memory_id="memory-1", relevance=0.9):
    return {
        "id": memory_id,
        "type": "experience",
        "task": task,
        "summary": task,
        "solution": "Use the verified procedure and rerun its focused check.",
        "relevance_score": relevance,
        "verification_strength": 0.10,
    }


def results(memories):
    return {
        "confidence": 0.9,
        "strategy": "memory_guided",
        "skills": [],
        "experiences": memories,
        "mistakes": [],
        "principles": [],
        "reflections": [],
    }


with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_UTILITY_PATH"] = os.path.join(directory, "utility.jsonl")

    useful = apply_utility_policy(
        results([candidate("Fix required request field validation.")]),
        "Fix required request field validation.",
        owner="codex",
    )
    assert useful["experiences"][0]["utility_score"] >= 0.56
    assert useful["utility_diagnostic"]["selected"]

    irrelevant = apply_utility_policy(
        results([candidate("Publish a Python package release.")]),
        "Fix required request field validation.",
        owner="codex",
    )
    assert irrelevant["experiences"] == []
    assert irrelevant["strategy"] == "normal_reasoning"
    assert "no decision or action alignment" in irrelevant["utility_diagnostic"]["withheld"][0]["reasons"]

    receipt = build_receipt("Fix required request field validation.", useful)
    save_receipt(receipt, "codex")
    record_feedback(receipt["id"], "harmful", owner="codex", reason="Wrong schema.")
    corrected = apply_utility_policy(
        results([candidate("Fix required request field validation.")]),
        "Fix required request field validation.",
        owner="codex",
    )
    assert corrected["experiences"] == []
    assert "misleading or harmful" in corrected["utility_diagnostic"]["withheld"][0]["reasons"][0]

    del os.environ["MEMCODER_UTILITY_PATH"]

print("PASS: utility engine")
