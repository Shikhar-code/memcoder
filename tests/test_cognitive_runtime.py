import os
import tempfile
import json

from memory.runtime import build_cognitive_packet, checkpoint_task_state, read_task_state


def memory(memory_type="experience"):
    return {
        "id": "memory-1",
        "type": memory_type,
        "task": "Validate a required request field.",
        "summary": "Missing fields caused an unexpected exception.",
        "solution": "Validate the field before string processing.",
        "files": ["request.py"],
        "retrieval_confidence": 0.82,
        "record_state": "trusted",
        "proof": {
            "record_state": "trusted",
            "applicability": "current",
            "evidence": [{"relation": "qa_verdict", "value": "approved"}],
            "conditions": ["Confirm the current request schema matches."],
            "risks": ["The input type may differ."],
            "required_verification": ["Run: python test_request.py"],
        },
    }


empty = {
    "confidence": 0.0,
    "strategy": "normal_reasoning",
    "skills": [],
    "experiences": [],
    "mistakes": [],
    "principles": [],
    "reflections": [],
}
none_packet = build_cognitive_packet("Investigate an unknown failure.", empty)
assert none_packet["intervention"]["mode"] == "none"
assert none_packet["belief_state"]["hypotheses"] == []

guided = {**empty, "confidence": 0.82, "strategy": "memory_guided", "experiences": [memory()]}
brief_packet = build_cognitive_packet(
    "Fix required field validation.",
    guided,
    environment={"project_id": "current"},
)
assert brief_packet["intervention"]["mode"] == "brief"
assert brief_packet["task_archetype"] == "validation"
assert brief_packet["transfer_delta"]["required_verification"][0].startswith("Run:")
assert brief_packet["prediction"]["falsifiers"]
assert brief_packet["belief_state"]["verified_facts"]
assert brief_packet["budget"]["within_budget"]
assert brief_packet["reuse_check"]["required_before_edit"]
assert build_cognitive_packet("Fix a video render.", empty)["task_archetype"] == "rendering"

skill = memory("skill")
skill["skill_definition"] = json.dumps({
    "schema_version": 1,
    "name": "Required field validation",
    "when_to_use": "A required field may be missing.",
    "inputs": ["request"],
    "steps": ["Check the field.", "Raise the expected error."],
    "verification": ["Run the focused test."],
    "supporting_experience_ids": ["experience-1"],
    "supporting_principle_ids": [],
    "human_approved": True,
    "version": 1,
})
planned = build_cognitive_packet("Plan validation work.", {**empty, "skills": [skill]})
assert planned["intervention"]["mode"] == "plan"
assert planned["plan"]["mode"] == "skill_guided"

with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_TASK_STATE_PATH"] = os.path.join(directory, "state.jsonl")
    first = checkpoint_task_state(
        "task-1", "codex", {"facts": ["The test fails."], "constraints": ["Small change."]}
    )
    second = checkpoint_task_state(
        "task-1", "codex", {"decisions": ["Validate before access."], "facts": ["The test fails."]}
    )
    assert first["id"].startswith("checkpoint_")
    assert second["state"]["facts"] == ["The test fails."]
    assert read_task_state("task-1", "codex")["state"]["decisions"] == [
        "Validate before access."
    ]
    del os.environ["MEMCODER_TASK_STATE_PATH"]

print("PASS: cognitive intervention runtime")
