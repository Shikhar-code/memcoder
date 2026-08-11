"""Build bounded, provider-free execution plans from retrieved cognition."""

import hashlib
import json

from memory.skills import skill_definition


PLAN_SCHEMA_VERSION = 1
MAX_PROCEDURE_STEPS = 4


def _text(value):
    return " ".join(str(value or "").split())


def _skill_plan(problem, skill, definition, environment=None):
    from memory.skill_intelligence import compile_transfer

    transfer = compile_transfer(definition, problem, environment=environment)
    procedure = transfer.get("reusable_steps", [])[:MAX_PROCEDURE_STEPS]
    steps = [
        {
            "order": index,
            "action": _text(instruction),
            "source": "skill",
            "completion_condition": "Complete this procedure step in the current project.",
        }
        for index, instruction in enumerate(procedure, start=1)
    ]
    steps.append({
        "order": len(steps) + 1,
        "action": "Run the skill's required verification in the current project.",
        "source": "skill_verification",
        "completion_condition": "All listed skill verification requirements have passed.",
        "verification": definition.get("verification", []),
    })
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "mode": "skill_guided",
        "goal": _text(problem),
        "strategy": "apply_validated_skill",
        "source_skill": {
            "id": skill.get("id", ""),
            "name": definition["name"],
            "when_to_use": definition["when_to_use"],
            "supporting_experience_ids": definition.get("supporting_experience_ids", []),
            "supporting_principle_ids": definition.get("supporting_principle_ids", []),
            "health": skill.get("health"),
        },
        "inputs": definition.get("inputs", []),
        "transfer": transfer,
        "steps": steps,
        "replan_if": [
            "The current project contradicts a skill assumption.",
            "A required verification check fails.",
            "The requested goal changes materially.",
        ],
        "recording_rule": "Record an outcome only after MemCoder QA approves host-supplied evidence.",
    }


def _foundation_plan(problem):
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "mode": "foundation",
        "goal": _text(problem),
        "strategy": "normal_reasoning",
        "source_skill": None,
        "inputs": [],
        "steps": [
            {
                "order": 1,
                "action": "Inspect the current project, the relevant input, and the expected behavior.",
                "source": "foundation",
                "completion_condition": "The actual failure or requested behavior is understood.",
            },
            {
                "order": 2,
                "action": "Make the smallest change that addresses the verified cause.",
                "source": "foundation",
                "completion_condition": "The change is scoped to the verified cause.",
            },
            {
                "order": 3,
                "action": "Run a focused host test, build, assertion, or documented review.",
                "source": "foundation_verification",
                "completion_condition": "Host-supplied evidence shows the result passed.",
            },
        ],
        "replan_if": [
            "Investigation disproves the initial cause.",
            "The focused verification fails.",
            "The requested goal changes materially.",
        ],
        "recording_rule": "Record an outcome only after MemCoder QA approves host-supplied evidence.",
    }


def _with_plan_id(plan):
    """Attach a stable identifier so a host can report a later outcome."""
    canonical = json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    plan["id"] = "plan_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
    return plan


def build_action_plan(problem, results, environment=None):
    """Use a retrieved promoted skill or return a transparent fallback plan.

    The function deliberately does not invent procedures with an LLM. A
    skill-guided plan is possible only when retrieval produced a valid skill.
    """
    for skill in results.get("skills", []):
        definition = skill_definition(skill)
        if isinstance(definition, dict) and definition.get("name") and definition.get("steps"):
            return _with_plan_id(_skill_plan(problem, skill, definition, environment=environment))
    return _with_plan_id(_foundation_plan(problem))
