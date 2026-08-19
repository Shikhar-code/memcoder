"""Build bounded, provider-free cognition briefs for agent hosts."""

import json
import math


BRIEF_TOKEN_BUDGET = 450
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
    proof = memory.get("proof") if isinstance(memory.get("proof"), dict) else {}
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
        # The full proof belongs in detail mode. Keep only a tiny status signal
        # here so the default cognition brief remains inside its token budget.
        "proof_status": (
            f"{proof.get('record_state', 'trusted')}/{proof.get('applicability', 'unknown')}"
            if proof else None
        ),
    }


def _decision_card(memory, memory_type):
    """Project one trusted memory into an action, its limits, and its proof."""
    if not memory:
        return None
    proof = memory.get("proof") if isinstance(memory.get("proof"), dict) else {}
    evidence = proof.get("evidence", []) if isinstance(proof.get("evidence"), list) else []
    recommendation = _compact_text(
        memory.get("solution") or memory.get("summary") or memory.get("task"),
        200,
    )
    return {
        "memory_id": memory.get("id", ""),
        "type": memory_type,
        "recommendation": recommendation,
        "applies_when": [
            _compact_text(item, 120) for item in proof.get("conditions", [])[:2]
        ] or ["The current project matches the retrieved task and environment."],
        "do_not_apply_when": [
            _compact_text(item, 120) for item in proof.get("risks", [])[:2]
        ] or ["Current-project evidence contradicts the retrieved guidance."],
        "failure_prevented": _compact_text(
            memory.get("summary") or f"Repeating the verified {memory_type} failure pattern.",
            150,
        ),
        "verification": _compact_text(
            (proof.get("required_verification") or [
                "Run the narrowest current-project verification."
            ])[0],
            150,
        ),
        "evidence_refs": [
            item.get("record_id") or item.get("value")
            for item in evidence[:3] if isinstance(item, dict)
        ] or [memory.get("id", "")],
        "confidence": memory.get("utility_score", memory.get("retrieval_confidence")),
    }


def _recommended_next_action(results):
    skills = results.get("skills", [])
    experiences = results.get("experiences", [])
    mistakes = results.get("mistakes", [])
    principles = results.get("principles", [])
    candidates = skills or experiences or mistakes or principles
    if candidates:
        verification = candidates[0].get("proof", {}).get("required_verification", [])
        if verification:
            return f"Use the retrieved guidance as a hypothesis; first verify: {verification[0]}"
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
    primary = None
    for memory_type, key in (
            ("skill", "skills"),
            ("experience", "experiences"),
            ("mistake", "mistakes"),
            ("principle", "principles"),
            ("reflection", "reflections")):
        memories = results.get(key, [])
        if memories:
            if primary is None:
                primary = (memories[0], memory_type)
            evidence.append(_card(memories[0], memory_type))

    brief = {
        "problem": _compact_text(problem, limit=280),
        "strategy": results.get("strategy", "normal_reasoning"),
        "recommended_next_action": _recommended_next_action(results),
        "decision_card": _decision_card(*primary) if primary else None,
        "evidence": evidence,
        "retrieval": results.get("retrieval", {"backend": "unknown"}),
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
