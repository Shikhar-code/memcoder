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
        "source": memory.get("source", ""),
        "source_experience_id": memory.get("source_experience_id", ""),
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
        detail_level="brief"):
    """Retrieve trusted guidance before an independent host starts work."""
    from memory.hierarchical_search import hierarchical_search
    from memory.brief import build_decision_brief

    if detail_level not in {"brief", "full"}:
        raise ValueError("detail_level must be 'brief' or 'full'.")

    results = hierarchical_search(
        problem,
        agent_id=agent_id,
        include_shared=include_shared,
        include_skills=include_skills,
    )

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


def plan_cognition(problem, agent_id="automation", include_shared=True):
    """Return one bounded plan grounded in retrieved QA-backed skills when available."""
    from memory.hierarchical_search import hierarchical_search
    from memory.brief import build_decision_brief
    from memory.plans import build_action_plan

    results = hierarchical_search(
        problem,
        agent_id=agent_id,
        include_shared=include_shared,
    )
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


def start_cognition(problem, agent_id="automation", include_shared=True):
    """Return the compact brief and bounded plan in one retrieval operation.

    This is the default host entry point for automated integrations. It avoids
    duplicate embedding/retrieval work while keeping ``prepare`` and ``plan``
    available for hosts that need their separate contracts.
    """
    from memory.hierarchical_search import hierarchical_search
    from memory.brief import build_decision_brief
    from memory.plans import build_action_plan

    results = hierarchical_search(
        problem,
        agent_id=agent_id,
        include_shared=include_shared,
    )
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
        agent_id="automation"):
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
