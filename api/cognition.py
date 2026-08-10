"""Provider-free cognition operations shared by MCP and automation hosts."""

def compact_memory(memory):
    """Return the stable, serializable memory shape exposed to hosts."""
    return {
        "id": memory.get("id", ""),
        "task": memory.get("task", ""),
        "summary": memory.get("summary", ""),
        "solution": memory.get("solution", ""),
        "files": memory.get("files", []),
        "distance": memory.get("score"),
        "confidence": memory.get("retrieval_confidence"),
        "utility_score": memory.get("utility_score"),
        "decision_overlap": memory.get("decision_overlap", 0),
        "source": memory.get("source", ""),
        "source_experience_id": memory.get("source_experience_id", ""),
        "provenance": memory.get("provenance", []),
        "record_state": memory.get("record_state", "trusted"),
        "applicability": memory.get("applicability", "unknown"),
        "validity_reason": memory.get("validity_reason", ""),
        "proof": memory.get("proof", {}),
        "skill": _skill_definition(memory),
        "skill_health": memory.get("health") if memory.get("type") == "skill" else None,
    }


def _skill_definition(memory):
    if memory.get("type") != "skill":
        return None
    from memory.skills import skill_definition
    return skill_definition(memory)


def prepare_cognition(
        problem,
        agent_id="automation",
        include_shared=True,
        include_skills=True,
        detail_level="brief",
        environment=None):
    """Retrieve trusted guidance before an independent host starts work."""
    from memory.hierarchical_search import hierarchical_search
    from memory.brief import build_decision_brief

    if detail_level not in {"brief", "full"}:
        raise ValueError("detail_level must be 'brief' or 'full'.")

    retrieval_options = {
        "agent_id": agent_id,
        "include_shared": include_shared,
        "include_skills": include_skills,
    }
    if environment is not None:
        retrieval_options["environment"] = environment
    results = hierarchical_search(problem, **retrieval_options)

    response = {
        "problem": problem,
        "include_shared": include_shared,
        "include_skills": include_skills,
        "confidence": results["confidence"],
        "strategy": results["strategy"],
        "detail_level": detail_level,
        "brief": build_decision_brief(problem, results),
        "available_detail": {
            key: len(results.get(key, []))
            for key in ("skills", "experiences", "mistakes", "principles", "reflections")
        },
        "instructions": [
            "Use trusted memories as investigation guidance, not proof.",
            "Start from the compact decision brief; request full detail only when needed.",
            "If no trusted memory is present, solve normally.",
            "Record an outcome only after QA approves host-supplied verification evidence."
        ]
    }
    if detail_level == "full":
        for key in ("skills", "experiences", "mistakes", "principles", "reflections"):
            response[key] = [compact_memory(memory) for memory in results.get(key, [])]
    return response


def plan_cognition(problem, agent_id="automation", include_shared=True, environment=None):
    """Return one bounded plan grounded in retrieved QA-backed skills when available."""
    from memory.hierarchical_search import hierarchical_search
    from memory.brief import build_decision_brief
    from memory.plans import build_action_plan

    retrieval_options = {"agent_id": agent_id, "include_shared": include_shared}
    if environment is not None:
        retrieval_options["environment"] = environment
    results = hierarchical_search(problem, **retrieval_options)
    return {
        "problem": problem,
        "include_shared": include_shared,
        "confidence": results["confidence"],
        "retrieval_strategy": results["strategy"],
        "brief": build_decision_brief(problem, results),
        "plan": build_action_plan(problem, results),
        "instructions": [
            "Treat the plan as guidance, not proof.",
            "Replan when a listed replan condition occurs.",
            "Record an outcome only after QA approves host-supplied verification evidence.",
        ],
    }


def start_cognition(problem, agent_id="automation", include_shared=True, environment=None):
    """Return the compact brief and bounded plan in one retrieval operation.

    This is the default host entry point for automated integrations. It avoids
    duplicate embedding/retrieval work while keeping ``prepare`` and ``plan``
    available for hosts that need their separate contracts.
    """
    from memory.hierarchical_search import hierarchical_search
    from memory.brief import build_decision_brief
    from memory.plans import build_action_plan

    retrieval_options = {"agent_id": agent_id, "include_shared": include_shared}
    if environment is not None:
        retrieval_options["environment"] = environment
    results = hierarchical_search(problem, **retrieval_options)
    return {
        "problem": problem,
        "include_shared": include_shared,
        "confidence": results["confidence"],
        "retrieval_strategy": results["strategy"],
        "brief": build_decision_brief(problem, results),
        "plan": build_action_plan(problem, results),
        "available_detail": {
            key: len(results.get(key, []))
            for key in ("skills", "experiences", "mistakes", "principles", "reflections")
        },
        "instructions": [
            "Follow the plan only while its assumptions fit the current project.",
            "Replan when a listed replan condition occurs.",
            "After success, record only QA-approved verification evidence.",
        ],
    }


def intervene_cognition(
        problem,
        agent_id="automation",
        include_shared=True,
        environment=None,
        token_budget=450):
    """Return the smallest useful, falsifiable cognition intervention."""
    from memory.hierarchical_search import hierarchical_search
    from memory.runtime import build_cognitive_packet

    retrieval_options = {"agent_id": agent_id, "include_shared": include_shared}
    if environment is not None:
        retrieval_options["environment"] = environment
    results = hierarchical_search(problem, **retrieval_options)
    packet = build_cognitive_packet(
        problem,
        results,
        environment=environment,
        token_budget=token_budget,
    )
    from memory.utility import save_receipt
    save_receipt(packet["receipt"], agent_id, environment=environment)
    return packet


def utility_feedback_cognition(
        intervention_id,
        rating,
        agent_id="automation",
        reason=None,
        action=None,
        outcome=None,
        mute=False,
        applicability_correction=None):
    """Record whether an exact intervention helped without changing memory validity."""
    from memory.utility import record_feedback
    return record_feedback(
        intervention_id=intervention_id,
        rating=rating,
        owner=agent_id,
        reason=reason,
        action=action,
        outcome=outcome,
        mute=mute,
        applicability_correction=applicability_correction,
    )


def retrieval_debug_cognition(
        problem,
        agent_id="automation",
        include_shared=True,
        environment=None,
        utility_threshold=None):
    """Explain semantic and utility ranking, gates, and withheld guidance."""
    from memory.hierarchical_search import hierarchical_search
    from memory.utility import frame_decision
    results = hierarchical_search(
        problem,
        agent_id=agent_id,
        include_shared=include_shared,
        environment=environment,
        utility_threshold=utility_threshold,
    )
    return {
        "problem": problem,
        "decision_frame": frame_decision(problem, environment=environment),
        "confidence": results["confidence"],
        "strategy": results["strategy"],
        "diagnostic": results["utility_diagnostic"],
    }


def project_update_cognition(project_id, update, agent_id="automation", environment=None):
    """Incrementally update bounded, owner-scoped project state and decisions."""
    from memory.project_cortex import update_project_state
    return update_project_state(project_id, agent_id, update, environment=environment)


def project_resurrect_cognition(
        project_id,
        agent_id="automation",
        environment=None,
        token_budget=600):
    """Return a bounded resume brief with stale decisions withheld."""
    from memory.project_cortex import resurrect_project
    return resurrect_project(
        project_id,
        agent_id,
        environment=environment,
        token_budget=token_budget,
    )


def project_handoff_cognition(project_id, agent_id="automation", environment=None):
    """Export a secret-scrubbed project cognition capsule."""
    from memory.project_cortex import export_handoff
    return export_handoff(project_id, agent_id, environment=environment)


def project_accept_cognition(capsule, agent_id="automation", environment=None):
    """Accept a bounded handoff while reporting environment drift."""
    from memory.project_cortex import accept_handoff
    return accept_handoff(capsule, agent_id, environment=environment)


def checkpoint_cognition(
        task_id,
        update,
        agent_id="automation",
        prediction_result=None):
    """Persist bounded working state without adding semantic guidance."""
    from memory.runtime import checkpoint_task_state

    return checkpoint_task_state(
        task_id=task_id,
        owner=agent_id,
        update=update,
        prediction_result=prediction_result,
    )


def task_state_cognition(task_id, agent_id="automation"):
    """Read the latest owner-scoped working-memory checkpoint."""
    from memory.runtime import read_task_state

    return {
        "task_id": task_id,
        "agent_id": agent_id,
        "checkpoint": read_task_state(task_id, agent_id),
    }


def plan_history_cognition(plan_id, agent_id="automation"):
    """Return read-only, owner-scoped audit history for a generated plan."""
    from memory.plan_outcomes import plan_outcome_history

    return {
        "plan_id": plan_id,
        "agent_id": agent_id,
        "outcomes": plan_outcome_history(plan_id, agent_id=agent_id),
    }


def skill_health_cognition(skill_id, agent_id="automation"):
    """Return a read-only, owner-scoped health calculation for one Skill."""
    from memory.skill_health import skill_health

    return skill_health(skill_id=skill_id, agent_id=agent_id)


def update_memory_validity_cognition(
        record_id,
        state,
        agent_id="automation",
        reason=None,
        environment=None):
    """Set lifecycle validity for one owner-scoped durable memory record."""
    from memory.validity import set_record_validity

    updated = set_record_validity(
        record_id=record_id,
        state=state,
        owner=agent_id,
        reason=reason,
        environment=environment,
    )
    return {
        "id": updated["record_id"],
        "record_state": updated["record_state"],
        "revision": updated["revision"],
        "environment": updated.get("environment", ""),
        "validity_reason": updated.get("validity_reason", ""),
    }


def retention_preview_cognition(agent_id=None, environment=None):
    """Preview exact-duplicate retention actions without changing memory."""
    from memory.retention import retention_preview

    return retention_preview(owner=agent_id, environment=environment)


def apply_retention_cognition(preview, agent_id=None):
    """Apply an explicitly reviewed, evidence-preserving retention preview."""
    from memory.retention import apply_retention_preview

    return apply_retention_preview(preview, owner=agent_id)


def trace_memory_cognition(record_id, agent_id=None):
    """Inspect a record's direct provenance edges and current durable state."""
    from memory.provenance import trace
    from memory.record_store import get_record

    record = get_record(record_id)
    if record is None:
        raise ValueError(f"Memory record was not found: {record_id}")
    if agent_id is not None and record.get("owner") != agent_id:
        raise ValueError("Memory record is not owned by this agent.")
    return {
        "id": record["record_id"],
        "record_state": record.get("record_state", "trusted"),
        "revision": record.get("revision", 1),
        "provenance": trace(record_id, owner=agent_id),
    }


def report_contradiction_cognition(first_id, second_id, reason, agent_id="automation"):
    """Record conflicting evidence and withhold both memories from automatic reuse."""
    from memory.contradictions import report_contradiction

    return report_contradiction(first_id, second_id, owner=agent_id, reason=reason)


def resolve_contradiction_cognition(winner_id, loser_id, reason, agent_id="automation"):
    """Resolve a reviewed contradiction without deleting either original record."""
    from memory.contradictions import resolve_contradiction

    return resolve_contradiction(winner_id, loser_id, owner=agent_id, reason=reason)


def evaluate_cognition(runs):
    """Summarize explicit baseline and MemCoder-assisted host evaluation runs."""
    from memory.evaluation import evaluate_runs

    return evaluate_runs(runs)


def record_cognition(
        task,
        files,
        summary,
        solution,
        reflection=None,
        principles=None,
        evidence=None,
        plan_id=None,
        applied_skill_id=None,
        agent_id="automation",
        environment=None):
    """QA an outcome and persist it only when the evidence is admitted."""
    from memory.record_outcome import record_outcome
    from memory.qa import evaluate_outcome_qa

    qa = evaluate_outcome_qa(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
        evidence=evidence,
        reflection=reflection,
        principles=principles,
    )

    recorded = record_outcome(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
        reflection=reflection,
        principles=principles,
        agent_id=agent_id,
        qa_report=qa,
        plan_id=plan_id,
        applied_skill_id=applied_skill_id,
        environment=environment,
    )

    return {
        "recorded": recorded,
        "experience_recorded": recorded["experience"] is not None,
        "rejected": recorded.get("rejected", []),
        "qa": qa,
        "plan_outcome": recorded.get("plan_outcome"),
    }


def verify_cognition(task, files, summary, solution, evidence, reflection=None, principles=None):
    """Return a QA verdict without storing memories or changing state."""
    from memory.qa import evaluate_outcome_qa

    return evaluate_outcome_qa(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
        evidence=evidence,
        reflection=reflection,
        principles=principles,
    )


def promote_skill_cognition(
        name,
        when_to_use,
        inputs,
        steps,
        verification,
        supporting_experience_ids,
        supporting_principle_ids=None,
        agent_id="automation",
        human_approved=False):
    """Promote QA-supported experience into one reusable, provider-free skill."""
    from memory.skills import promote_skill

    return promote_skill(
        name=name,
        when_to_use=when_to_use,
        inputs=inputs,
        steps=steps,
        verification=verification,
        supporting_experience_ids=supporting_experience_ids,
        supporting_principle_ids=supporting_principle_ids,
        agent_id=agent_id,
        human_approved=human_approved,
    )
