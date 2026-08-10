"""Decision-utility policy and append-only intervention feedback."""

import hashlib
import json
import os
from pathlib import Path

from memory.records import utc_now
from memory.relevance import query_terms


RATINGS = {"helpful", "ignored", "misleading", "harmful"}
THRESHOLDS = {
    "skill": 0.62,
    "experience": 0.56,
    "mistake": 0.52,
    "principle": 0.50,
    "reflection": 0.58,
}


def _path():
    configured = os.environ.get("MEMCODER_UTILITY_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_utility.jsonl"


def _events():
    path = _path()
    if not path.exists():
        return []
    events = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)
    return events


def _append(event):
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    stored = {**event, "timestamp": event.get("timestamp") or utc_now()}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(stored, sort_keys=True, ensure_ascii=False) + "\n")
    return stored


def frame_decision(problem, environment=None):
    """Describe the decision MemCoder is trying to improve, not just its topic."""
    from memory.runtime import classify_task

    archetype = classify_task(problem)
    risk = "high" if archetype in {"security", "debugging", "integration"} else "normal"
    return {
        "archetype": archetype,
        "decision": "Choose the next safe action for this task.",
        "desired_outcome": "Complete the requested work with current-project proof.",
        "failure_risk": risk,
        "constraints": list((environment or {}).get("constraints", []))[:4],
        "proof_need": "focused current-project verification",
    }


def _comparable(stored, current):
    stored, current = stored or {}, current or {}
    return all(
        key not in stored or key not in current or stored[key] == current[key]
        for key in ("project_id", "runtime", "language")
    )


def _feedback_adjustment(memory_id, owner, environment=None):
    feedback = [
        event
        for event in _events()
        if event.get("kind") == "feedback"
        and event.get("owner") == owner
        and memory_id in event.get("memory_ids", [])
        and _comparable(event.get("environment"), environment)
    ]
    ratings = [event.get("rating") for event in feedback]
    return max(-0.6, min(0.15,
        ratings.count("helpful") * 0.05
        - ratings.count("ignored") * 0.03
        - ratings.count("misleading") * 0.25
        - ratings.count("harmful") * 0.50
        - (1.0 if any(event.get("mute") for event in feedback) else 0.0)
    ))


def apply_utility_policy(results, problem, owner="automation", threshold=None, environment=None):
    """Rank trusted candidates by expected decision value and veto weak transfer."""
    from memory.runtime import classify_task

    query_archetype = classify_task(problem)
    query_words = query_terms(problem)
    diagnostic = {"query_archetype": query_archetype, "selected": [], "withheld": []}
    for key in ("skills", "experiences", "mistakes", "principles", "reflections"):
        selected = []
        for memory in results.get(key, []):
            candidate = dict(memory)
            memory_words = query_terms(" ".join((
                str(candidate.get("task", "")),
                str(candidate.get("summary", "")),
                str(candidate.get("solution", "")),
            )))
            overlap = len(query_words & memory_words)
            archetype_match = classify_task(candidate.get("task", "")) == query_archetype
            semantic = max(0.0, min(1.0, float(candidate.get("relevance_score", 0.0))))
            feedback = _feedback_adjustment(candidate.get("id", ""), owner, environment)
            score = round(
                semantic * 0.55
                + (0.16 if archetype_match else 0.0)
                + min(overlap, 3) * 0.05
                + min(float(candidate.get("verification_strength", 0.0)), 0.10)
                + feedback,
                2,
            )
            memory_type = candidate.get("type", key.rstrip("s"))
            required = float(threshold) if threshold is not None else THRESHOLDS.get(memory_type, 0.56)
            reasons = []
            if not overlap and not archetype_match:
                reasons.append("no decision or action alignment")
            if feedback <= -0.25:
                reasons.append("comparable feedback marked this guidance misleading or harmful")
            if score < required:
                reasons.append(f"utility {score:.2f} is below {required:.2f}")
            candidate["utility_score"] = score
            candidate["utility_feedback"] = round(feedback, 2)
            candidate["decision_overlap"] = overlap
            card = {
                "id": candidate.get("id", ""),
                "type": memory_type,
                "semantic_rank": candidate.get("relevance_score", 0.0),
                "utility_rank": score,
                "gate": "withheld" if reasons else "selected",
                "reasons": reasons or ["decision-aligned, trusted, and above threshold"],
            }
            if reasons:
                diagnostic["withheld"].append(card)
            else:
                selected.append(candidate)
                diagnostic["selected"].append(card)

        # Avoid spending host context on near-duplicate guidance.
        diverse = []
        signatures = set()
        for candidate in sorted(selected, key=lambda item: item["utility_score"], reverse=True):
            signature = " ".join(sorted(query_terms(candidate.get("solution") or candidate.get("task", ""))))
            if signature and signature in signatures:
                continue
            signatures.add(signature)
            diverse.append(candidate)
        results[key] = diverse

    selected = diagnostic["selected"]
    results["utility_diagnostic"] = diagnostic
    results["confidence"] = max((item["utility_rank"] for item in selected), default=0.0)
    results["strategy"] = "memory_guided" if selected else "normal_reasoning"
    return results


def build_receipt(problem, results, environment=None):
    selected = results.get("utility_diagnostic", {}).get("selected", [])
    material = json.dumps({
        "problem": problem,
        "memory_ids": [item.get("id") for item in selected],
        "environment": environment or {},
    }, sort_keys=True, ensure_ascii=False)
    intervention_id = "intervention_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:20]
    return {
        "id": intervention_id,
        "why_now": "Decision-aligned verified guidance cleared the utility gate." if selected else "No candidate cleared the utility gate.",
        "decision_changed": "Investigate retrieved evidence first." if selected else "None; solve normally.",
        "memory_ids": [item.get("id") for item in selected],
        "applicability": "current environment must still be verified",
        "expected_value": max((item.get("utility_rank", 0.0) for item in selected), default=0.0),
        "verification": "Host proof is required before learning.",
    }


def save_receipt(receipt, owner, environment=None):
    return _append({
        "kind": "receipt",
        "id": receipt["id"],
        "owner": owner,
        "memory_ids": receipt.get("memory_ids", []),
        "environment": environment or {},
    })


def record_feedback(
        intervention_id,
        rating,
        owner="automation",
        reason=None,
        action=None,
        outcome=None,
        mute=False,
        applicability_correction=None):
    if rating not in RATINGS:
        raise ValueError("rating must be helpful, ignored, misleading, or harmful.")
    receipt = next((
        event for event in reversed(_events())
        if event.get("kind") == "receipt"
        and event.get("id") == intervention_id
        and event.get("owner") == owner
    ), None)
    if receipt is None:
        raise ValueError("intervention receipt was not found for this agent.")
    return _append({
        "kind": "feedback",
        "id": "feedback_" + hashlib.sha256(
            f"{intervention_id}:{rating}:{utc_now()}".encode("utf-8")
        ).hexdigest()[:20],
        "intervention_id": intervention_id,
        "owner": owner,
        "memory_ids": receipt.get("memory_ids", []),
        "environment": receipt.get("environment", {}),
        "rating": rating,
        "reason": " ".join(str(reason or "").split())[:280],
        "action": " ".join(str(action or "").split())[:280],
        "outcome": " ".join(str(outcome or "").split())[:280],
        "mute": bool(mute),
        "applicability_correction": applicability_correction if isinstance(applicability_correction, dict) else None,
    })
