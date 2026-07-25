"""Plans must use only retrieved promoted skills or a transparent fallback."""

import json
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

from memory.plans import build_action_plan


skill = {
    "id": "skill-1",
    "type": "skill",
    "skill_definition": json.dumps({
        "schema_version": 1,
        "name": "Required field validation",
        "when_to_use": "A request might omit a required field before processing.",
        "inputs": ["request payload"],
        "steps": ["Check the field.", "Raise the expected error."],
        "verification": ["Run the focused validation test."],
        "supporting_experience_ids": ["experience-1", "experience-2"],
        "human_approved": False,
        "version": 1,
    }),
}

guided = build_action_plan(
    "Validate a required request field.",
    {"skills": [skill]},
)
assert guided["mode"] == "skill_guided"
assert guided["id"].startswith("plan_")
assert guided["source_skill"]["id"] == "skill-1"
assert guided["steps"][0]["action"] == "Check the field."
assert guided["steps"][-1]["verification"] == ["Run the focused validation test."]
assert len(guided["steps"]) <= 5

fallback = build_action_plan("Investigate an unknown issue.", {"skills": []})
assert fallback["mode"] == "foundation"
assert fallback["id"].startswith("plan_")
assert fallback["source_skill"] is None
assert fallback["steps"][-1]["source"] == "foundation_verification"

invalid = build_action_plan(
    "Validate something.",
    {"skills": [{"id": "broken", "skill_definition": "{}"}]},
)
assert invalid["mode"] == "foundation"

print("PASS: bounded cognition planning")
