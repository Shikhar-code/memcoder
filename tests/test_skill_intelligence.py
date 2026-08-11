import os
import tempfile

from memory.skill_intelligence import (
    causal_summary,
    compile_transfer,
    compose_skills,
    evolve_skill,
    record_causal_credit,
)


skill = {
    "name": "Safe dependency update",
    "when_to_use": "updating a Python dependency",
    "preconditions": ["Python project", "existing focused tests"],
    "steps": ["Inspect the lock file.", "Update the declared version."],
    "verification": ["Run the focused dependency tests."],
    "failure_handling": ["Stop if dependency resolution fails."],
    "rollback": ["Restore the prior dependency declaration."],
    "applicability_limits": ["JavaScript only project"],
    "state_mutations": ["dependencies:write"],
    "version": 1,
}

transfer = compile_transfer(skill, "Update a Python project dependency safely")
assert transfer["safe_to_apply"] is True
assert transfer["reusable_steps"] == skill["steps"]
assert "existing focused tests" in transfer["missing_conditions"]

conflict = compose_skills([skill, {
    "name": "Read dependency state",
    "steps": ["Inspect dependency state."],
    "verification": ["Confirm no changes."],
    "rollback": [],
    "state_mutations": ["dependencies:read"],
}])
assert conflict["compatible"] is False

evolved = evolve_skill(skill, {"steps": skill["steps"] + ["Inspect the result."]}, "demo")
assert evolved["candidate"]["version"] == 2
assert evolved["requires_review"] is True
assert evolved["candidate"]["project_overlays"]["demo"]

with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_SKILL_CREDIT_PATH"] = os.path.join(directory, "credit.jsonl")
    record_causal_credit("skill-1", "tester", "succeeded", "present_only")
    record_causal_credit(
        "skill-1", "tester", "succeeded", "changed_behavior", ["Added rollback check"]
    )
    summary = causal_summary("skill-1", "tester")
    assert summary["present"] == 2
    assert summary["influenced"] == 1
    assert summary["successful_influence"] == 1
    from memory.skill_health import skill_health
    health = skill_health("skill-1", "tester")
    assert health["status"] == "trusted"
    assert health["attempts"] == 1

os.environ.pop("MEMCODER_SKILL_CREDIT_PATH", None)
print("PASS: skill intelligence")
