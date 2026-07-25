"""Build bounded, provider-free cognition briefs for agent hosts."""

import json
import math


BRIEF_TOKEN_BUDGET = 350
CARD_TEXT_LIMIT = 180


def _compact_text(value, limit=CARD_TEXT_LIMIT):
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _estimate_tokens(value):
    """Conservative, dependency-free estimate for prompt-budget accounting."""
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return math.ceil(len(serialized) / 4)


def _card(memory, memory_type):
    health = memory.get("health") if memory_type == "skill" else None
    return {
        "id": memory.get("id", ""),
        "type": memory_type,
        "task": _compact_text(memory.get("task")),
        "guidance": _compact_text(
            memory.get("solution") or memory.get("summary") or memory.get("task")
        ),
        "files": list(memory.get("files", []))[:3],
        "confidence": memory.get("retrieval_confidence"),
        # A full health audit belongs in the plan/detail API, not the brief.
        "health": health.get("status") if isinstance(health, dict) else None,
    }


def _recommended_next_action(results):
    skills = results.get("skills", [])
    experiences = results.get("experiences", [])
    mistakes = results.get("mistakes", [])
    principles = results.get("principles", [])
    if skills:
        return "Use the retrieved skill as a procedure, then verify each required completion condition in the current project."
    if experiences:
        return "Investigate the closest verified experience first; treat its solution as a hypothesis and verify it in the current project."
    if mistakes:
        return "Start by checking the retrieved past mistake before making a change."
    if principles:
        return "Apply the retrieved principle only after confirming it fits the current project."
    return "No trusted memory is available; inspect the current project and solve normally."


def build_decision_brief(problem, results):
    """Return at most one high-value card per memory type plus a token budget."""
    evidence = []
    for memory_type, key in (
            ("skill", "skills"),
            ("experience", "experiences"),
            ("mistake", "mistakes"),
            ("principle", "principles"),
            ("reflection", "reflections")):
        memories = results.get(key, [])
        if memories:
            evidence.append(_card(memories[0], memory_type))

    brief = {
        "problem": _compact_text(problem, limit=280),
        "strategy": results.get("strategy", "normal_reasoning"),
        "recommended_next_action": _recommended_next_action(results),
        "evidence": evidence,
        "verification_requirement": "Verify the current result with a host test, build, assertion, or documented review before recording learning.",
    }
    estimated_tokens = _estimate_tokens(brief)
    return {
        **brief,
        "budget": {
            "estimated_tokens": estimated_tokens,
            "token_budget": BRIEF_TOKEN_BUDGET,
            "within_budget": estimated_tokens <= BRIEF_TOKEN_BUDGET,
        },
    }
