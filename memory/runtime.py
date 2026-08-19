"""Provider-free intervention policy and bounded cognitive task state."""

import hashlib
import json
import math
import os
from pathlib import Path

from memory.brief import build_decision_brief
from memory.plans import build_action_plan
from memory.records import utc_now


DEFAULT_TOKEN_BUDGET = 450
STATE_FIELDS = (
    "facts",
    "constraints",
    "decisions",
    "risks",
    "open_questions",
    "verification",
)


def _text(value, limit=220):
    value = " ".join(str(value or "").split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _json_object(value):
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value or "")
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _estimate_tokens(value):
    return math.ceil(len(json.dumps(value, ensure_ascii=False, separators=(",", ":"))) / 4)


def classify_task(problem):
    """Return a transparent task archetype without invoking a provider."""
    text = str(problem or "").lower()
    archetypes = (
        ("security", ("security", "secret", "credential", "vulnerab", "permission")),
        ("rendering", ("render", "animation", "video", "scene", "visual")),
        ("dependency", ("dependenc", "package", "install", "module not found", "version")),
        ("validation", ("validat", "required field", "exception", "reject")),
        ("integration", ("integrat", "adapter", "plugin", "mcp", "api")),
        ("debugging", ("bug", "fix", "fail", "error", "regression")),
        ("planning", ("plan", "roadmap", "sequence", "approach")),
        ("transformation", ("convert", "migrate", "transform", "rewrite")),
        ("documentation", ("readme", "document", "guide", "instructions")),
    )
    for archetype, terms in archetypes:
        if any(term in text for term in terms):
            return archetype
    return "general"


def choose_intervention(results, token_budget=DEFAULT_TOKEN_BUDGET):
    """Select the least expensive useful intervention."""
    if results.get("skills"):
        mode = "plan"
        reason = "A healthy promoted skill can supply a verified procedure."
    elif results.get("experiences"):
        mode = "brief"
        reason = "A relevant verified experience can guide investigation."
    elif results.get("mistakes") or results.get("principles") or results.get("reflections"):
        mode = "risk"
        reason = "Only cautionary guidance is available; avoid asserting a solution."
    else:
        mode = "none"
        reason = "No trusted relevant memory is available."
    if token_budget < 120 and mode in {"brief", "plan"}:
        return {"mode": "risk", "reason": "The host budget allows only a compact warning."}
    return {"mode": mode, "reason": reason}


def _primary_memory(results):
    for key in ("skills", "experiences", "mistakes", "principles", "reflections"):
        if results.get(key):
            return key[:-1] if key != "experiences" else "experience", results[key][0]
    return None, None


def build_transfer_delta(memory, environment=None):
    """Explain what transfers, what differs, and what must be re-verified."""
    if not memory:
        return None
    proof = memory.get("proof") if isinstance(memory.get("proof"), dict) else {}
    stored = _json_object(memory.get("environment"))
    current = environment or {}
    matches = []
    differences = []
    for key in ("project_id", "fingerprint", "runtime", "language"):
        if key not in stored or key not in current:
            continue
        if stored[key] == current[key]:
            matches.append(f"{key} matches the verified environment.")
        else:
            differences.append(f"{key} differs from the verified environment.")
    if not stored:
        differences.append("The source memory has no environment fingerprint.")
    elif not current:
        differences.append("The current environment was not supplied.")
    return {
        "matches": matches,
        "differences": differences,
        "safe_reuse": _text(memory.get("solution") or memory.get("summary") or memory.get("task")),
        "assumptions": [_text(item) for item in proof.get("conditions", [])[:2]],
        "risks": [_text(item) for item in proof.get("risks", [])[:2]],
        "required_verification": [
            _text(item) for item in proof.get("required_verification", [])[:2]
        ] or ["Verify the result in the current project before recording learning."],
    }


def _prediction(memory, transfer_delta):
    if not memory:
        return {
            "expected_outcome": "Normal reasoning should produce a result that passes host verification.",
            "assumptions": [],
            "falsifiers": ["The focused host verification fails."],
            "verification": ["Run a focused host test, build, assertion, or documented review."],
            "confidence": 0.0,
        }
    return {
        "expected_outcome": "Applying the retrieved guidance should reduce the closest known failure risk.",
        "assumptions": transfer_delta["assumptions"],
        "falsifiers": transfer_delta["differences"][:1] + [
            "The required current-project verification fails."
        ],
        "verification": transfer_delta["required_verification"],
        "confidence": memory.get("retrieval_confidence", 0.0),
    }


def _belief_state(memory, transfer_delta):
    if not memory:
        return {"verified_facts": [], "hypotheses": [], "risks": []}
    proof = memory.get("proof") if isinstance(memory.get("proof"), dict) else {}
    facts = []
    if proof.get("record_state") == "trusted":
        facts.append("The retrieved record is currently trusted by MemCoder's admission policy.")
    if proof.get("evidence"):
        facts.append("The retrieved record carries stored verification or provenance evidence.")
    return {
        "verified_facts": facts,
        "hypotheses": [transfer_delta["safe_reuse"]] if transfer_delta.get("safe_reuse") else [],
        "risks": transfer_delta["risks"] + transfer_delta["differences"],
    }


def _compact_packet(packet, token_budget):
    if _estimate_tokens(packet) <= token_budget:
        return packet
    packet["detail_level"] = "nudge"
    brief = packet.get("guidance", {})
    packet["guidance"] = {
        "recommended_next_action": _text(brief.get("recommended_next_action"), 160),
        "evidence": [
            {
                "id": card.get("id", ""),
                "type": card.get("type", ""),
                "guidance": _text(card.get("guidance"), 120),
            }
            for card in brief.get("evidence", [])[:1]
        ],
    }
    if packet.get("plan"):
        plan = packet["plan"]
        packet["plan"] = {
            "id": plan.get("id"),
            "mode": plan.get("mode"),
            "next_step": _text((plan.get("steps") or [{}])[0].get("action"), 150),
            "verification": _text((plan.get("steps") or [{}])[-1].get("completion_condition"), 150),
        }
    delta = packet.get("transfer_delta") or {}
    packet["transfer_delta"] = {
        "safe_reuse": _text(delta.get("safe_reuse"), 120),
        "differences": delta.get("differences", [])[:1],
        "risks": delta.get("risks", [])[:1],
        "required_verification": delta.get("required_verification", [])[:1],
    } if delta else None
    packet["belief_state"] = {
        key: values[:1] for key, values in packet["belief_state"].items()
    }
    packet["prediction"] = {
        "expected_outcome": _text(packet["prediction"]["expected_outcome"], 120),
        "falsifiers": packet["prediction"]["falsifiers"][:1],
        "verification": packet["prediction"]["verification"][:1],
        "confidence": packet["prediction"]["confidence"],
    }
    diagnostic = packet.get("retrieval_debug", {})
    packet["retrieval_debug"] = {
        "selected": diagnostic.get("selected", [])[:1],
        "withheld": diagnostic.get("withheld", [])[:1],
    }
    frame = packet.get("decision_frame", {})
    packet["decision_frame"] = {
        "archetype": frame.get("archetype"),
        "failure_risk": frame.get("failure_risk"),
        "proof_need": frame.get("proof_need"),
    }
    if _estimate_tokens(packet) > token_budget:
        packet["guidance"] = {
            "recommended_next_action": packet.get("guidance", {}).get("recommended_next_action", "")
        }
        receipt = packet.get("receipt", {})
        packet["receipt"] = {
            "id": receipt.get("id"),
            "why_now": receipt.get("why_now"),
            "decision_changed": receipt.get("decision_changed"),
            "memory_ids": receipt.get("memory_ids", [])[:2],
            "known_differences": receipt.get("known_differences", [])[:1],
            "expected_value": receipt.get("expected_value", 0.0),
            "token_cost_budget": receipt.get("token_cost_budget"),
            "verification": receipt.get("verification"),
        }
        packet["reuse_check"] = {
            "required_before_edit": True,
            "smallest_safe_action": packet.get("reuse_check", {}).get("smallest_safe_action"),
        }
        if packet.get("transfer_delta"):
            packet["transfer_delta"] = {
                "required_verification": packet["transfer_delta"].get("required_verification", [])[:1]
            }
    return packet


def _with_budget(packet, token_budget):
    """Attach stable accounting that includes its own serialized cost."""
    result = dict(packet)
    estimated = 0
    for _ in range(3):
        result["budget"] = {
            "estimated_tokens": estimated,
            "token_budget": token_budget,
            "within_budget": estimated <= token_budget,
        }
        updated = _estimate_tokens(result)
        if updated == estimated:
            break
        estimated = updated
    result["budget"] = {
        "estimated_tokens": estimated,
        "token_budget": token_budget,
        "within_budget": estimated <= token_budget,
    }
    return result


def enforce_token_budget(packet, token_budget=DEFAULT_TOKEN_BUDGET):
    """Return a useful packet that never exceeds the host's declared budget."""
    token_budget = max(80, int(token_budget))
    fitted = _with_budget(_compact_packet(dict(packet), token_budget), token_budget)
    if fitted["budget"]["within_budget"]:
        return fitted

    receipt = packet.get("receipt") or {}
    prediction = packet.get("prediction") or {}
    guidance = packet.get("guidance") or {}
    plan = packet.get("plan") or {}
    compact = {
        "schema_version": packet.get("schema_version", 1),
        "problem": _text(packet.get("problem"), 100),
        "task_archetype": packet.get("task_archetype", "general"),
        "intervention": packet.get("intervention", {"mode": "none"}),
        "guidance": {
            "recommended_next_action": _text(
                guidance.get("recommended_next_action"), 120
            )
        },
        "prediction": {
            "falsifiers": prediction.get("falsifiers", [])[:1],
            "verification": prediction.get("verification", [])[:1],
            "confidence": prediction.get("confidence", 0.0),
        },
        "receipt": {
            "id": receipt.get("id"),
            "memory_ids": receipt.get("memory_ids", [])[:1],
            "expected_value": receipt.get("expected_value", 0.0),
            "verification": "Host proof is required before learning.",
        },
    }
    if plan:
        compact["plan"] = {
            "id": plan.get("id"),
            "mode": plan.get("mode"),
            "next_step": _text(
                plan.get("next_step") or (plan.get("steps") or [{}])[0].get("action"),
                100,
            ),
            "verification": _text(
                plan.get("verification")
                or (plan.get("steps") or [{}])[-1].get("completion_condition"),
                100,
            ),
        }
    fitted = _with_budget(compact, token_budget)
    if fitted["budget"]["within_budget"]:
        return fitted

    # An extremely small budget cannot carry trustworthy guidance. Abstain,
    # but preserve the receipt so feedback and lifecycle accounting still work.
    return _with_budget({
        "intervention": {
            "mode": "none",
            "reason": "The host token budget is too small for verified guidance.",
        },
        "receipt": {"id": receipt.get("id")},
    }, token_budget)


def build_cognitive_packet(problem, results, environment=None, token_budget=DEFAULT_TOKEN_BUDGET):
    """Compile one bounded host-facing packet from already trusted retrieval results."""
    token_budget = max(80, int(token_budget))
    intervention = choose_intervention(results, token_budget=token_budget)
    memory_type, memory = _primary_memory(results)
    delta = build_transfer_delta(memory, environment=environment)
    from memory.utility import build_receipt, frame_decision
    packet = {
        "schema_version": 1,
        "problem": _text(problem, 280),
        "task_archetype": classify_task(problem),
        "intervention": intervention,
        "detail_level": "brief",
        "confidence": max(
            results.get("confidence", 0.0),
            (memory or {}).get("retrieval_confidence", 0.0),
        ),
        "source": {
            "id": memory.get("id", ""),
            "type": memory_type,
        } if memory else None,
        "belief_state": _belief_state(memory, delta) if delta else {
            "verified_facts": [], "hypotheses": [], "risks": []
        },
        "transfer_delta": delta,
        "prediction": _prediction(memory, delta),
        "reuse_check": {
            "required_before_edit": True,
            "checks": [
                "Confirm the current project does not already satisfy the requirement.",
                "Prefer an existing project pattern, standard-library feature, or installed dependency when it is sufficient.",
            ],
            "smallest_safe_action": "Reuse existing behavior when verified; otherwise make the smallest scoped change.",
        },
        "guidance": build_decision_brief(problem, results),
        "plan": build_action_plan(problem, results, environment=environment) if intervention["mode"] == "plan" else None,
        "decision_frame": frame_decision(problem, environment=environment),
        "receipt": build_receipt(problem, results, environment=environment),
        "retrieval_debug": results.get("utility_diagnostic", {"selected": [], "withheld": []}),
    }
    packet["receipt"]["supporting_evidence"] = packet["receipt"].get("memory_ids", [])[:3]
    packet["receipt"]["known_differences"] = (delta or {}).get("differences", [])[:2]
    packet["receipt"]["token_cost_budget"] = token_budget
    return enforce_token_budget(packet, token_budget)


def _state_path():
    configured = os.environ.get("MEMCODER_TASK_STATE_PATH")
    if configured:
        return Path(configured)
    from memory.chroma_client import db_path
    return Path(db_path).parent / "memcoder_task_state.jsonl"


def _history(task_id, owner):
    path = _state_path()
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("task_id") == task_id and entry.get("owner") == owner:
                entries.append(entry)
    return entries


def read_task_state(task_id, owner):
    history = _history(task_id, owner)
    return history[-1] if history else None


def checkpoint_task_state(task_id, owner, update, prediction_result=None):
    """Persist a bounded, non-semantic checkpoint for a long-running task."""
    if not isinstance(update, dict):
        raise ValueError("checkpoint update must be an object.")
    previous = read_task_state(task_id, owner) or {}
    state = {}
    for field in STATE_FIELDS:
        old = previous.get("state", {}).get(field, [])
        new = update.get(field, [])
        if not isinstance(new, list):
            raise ValueError(f"checkpoint field '{field}' must be a list.")
        merged = []
        for item in [*old, *new]:
            item = _text(item, 280)
            if item and item not in merged:
                merged.append(item)
        state[field] = merged[-8:]
    stored = {
        "task_id": _text(task_id, 160),
        "owner": _text(owner, 120),
        "state": state,
        "prediction_result": prediction_result if isinstance(prediction_result, dict) else None,
        "timestamp": utc_now(),
    }
    canonical = json.dumps(stored, sort_keys=True, ensure_ascii=False)
    stored["id"] = "checkpoint_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(stored, sort_keys=True, ensure_ascii=False) + "\n")
    return stored
