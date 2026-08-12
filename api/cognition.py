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

    from memory.failure_frontier import match_frontiers
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
        "failure_frontier": match_frontiers(
            problem, owner=agent_id, environment=environment, limit=3
        ),
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
        "plan": build_action_plan(problem, results, environment=environment),
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
        "plan": build_action_plan(problem, results, environment=environment),
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
    from memory.failure_frontier import match_frontiers
    packet["failure_frontier"] = match_frontiers(
        problem, owner=agent_id, environment=environment, limit=3
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


def utility_feedback_summary_cognition(memory_id=None, agent_id=None, environment=None):
    """Return outcome calibration without changing a trusted record."""
    from memory.utility import feedback_summary
    return feedback_summary(memory_id=memory_id, owner=agent_id, environment=environment)


def failure_frontier_cognition(
        action="match",
        problem=None,
        trigger=None,
        risk=None,
        warning=None,
        verification=None,
        owner="automation",
        environment=None,
        counterexamples=None,
        source_memory_ids=None,
        frontier_id=None,
        status=None,
        outcome=None,
        reason=None,
        limit=5):
    """Record, retrieve, and calibrate append-only failure-frontier warnings."""
    from memory.failure_frontier import (
        feedback_frontier,
        list_frontiers,
        match_frontiers,
        record_frontier,
        update_frontier,
    )
    if action == "record":
        return record_frontier(
            trigger=trigger, risk=risk, warning=warning, verification=verification,
            owner=owner, environment=environment, counterexamples=counterexamples,
            source_memory_ids=source_memory_ids, status=status or "active",
        )
    if action == "match":
        return {"matches": match_frontiers(problem, owner=owner, environment=environment, limit=limit)}
    if action == "list":
        return {"frontiers": list_frontiers(owner=owner, status=status)}
    if action == "update":
        return update_frontier(frontier_id, status, owner=owner, reason=reason)
    if action == "feedback":
        return feedback_frontier(frontier_id, outcome, owner=owner, reason=reason)
    raise ValueError("action must be record, match, list, update, or feedback.")


def cognitive_branch_cognition(
        action="list",
        branch_id=None,
        target_branch_id=None,
        name=None,
        owner="automation",
        project_id=None,
        environment=None,
        base_environment=None,
        base_ref=None,
        kind=None,
        key=None,
        before=None,
        after=None,
        memory_ids=None,
        obligation_id=None,
        obligation_name=None,
        obligation_kind="test",
        command=None,
        passed=None,
        evidence=None,
        apply=False,
        reason=None,
        status=None):
    """Manage branch-local cognitive hypotheses and proof-gated merges."""
    from memory.cognitive_branch import (
        add_proof_obligation,
        cognitive_diff,
        complete_proof_obligation,
        create_branch,
        list_branches,
        merge_branch,
        record_change,
        rollback_branch,
    )
    if action == "create":
        return create_branch(name, owner=owner, project_id=project_id,
                             base_environment=base_environment or environment, base_ref=base_ref)
    if action == "list":
        return {"branches": list_branches(owner=owner, status=status)}
    if action == "change":
        return record_change(branch_id, kind, key, before=before, after=after,
                             owner=owner, memory_ids=memory_ids)
    if action == "obligation":
        return add_proof_obligation(branch_id, obligation_name, kind=obligation_kind,
                                    command=command, owner=owner)
    if action == "verify":
        return complete_proof_obligation(branch_id, obligation_id, passed, evidence, owner=owner)
    if action == "diff":
        return cognitive_diff(branch_id, target_branch_id=target_branch_id, owner=owner)
    if action == "merge":
        return merge_branch(branch_id, owner=owner, target_branch_id=target_branch_id,
                            environment=environment, apply=apply)
    if action == "rollback":
        return rollback_branch(branch_id, owner=owner, reason=reason)
    raise ValueError("action must be create, list, change, obligation, verify, diff, merge, or rollback.")


def autopilot_event_cognition(
        event,
        task_id,
        problem,
        agent_id="automation",
        include_shared=True,
        environment=None,
        context=None,
        action=None,
        outcome=None,
        token_budget=450):
    """Handle one host lifecycle boundary; host work always fails open."""
    try:
        from memory.autopilot import begin_event, finish_event

        decision = begin_event(
            event=event,
            task_id=task_id,
            owner=agent_id,
            problem=problem,
            context=context,
            action=action,
            environment=environment,
        )
        from memory.failure_frontier import match_frontiers
        decision["failure_frontier"] = match_frontiers(
            problem, owner=agent_id, environment=environment, limit=3
        )
        intervention = None
        if decision["should_intervene"]:
            intervention = intervene_cognition(
                problem=problem,
                agent_id=agent_id,
                include_shared=include_shared,
                environment=environment,
                token_budget=token_budget,
            )

        capture = None
        if event in {"verification_finished", "task_completed"} and isinstance(outcome, dict):
            capture_result = record_cognition(
                task=outcome.get("task", problem),
                files=outcome.get("files", []),
                summary=outcome.get("summary", ""),
                solution=outcome.get("solution", ""),
                reflection=outcome.get("reflection"),
                principles=outcome.get("principles"),
                evidence=outcome.get("evidence"),
                plan_id=outcome.get("plan_id"),
                applied_skill_id=outcome.get("applied_skill_id"),
                agent_id=agent_id,
                environment=environment,
            )
            recorded = capture_result.get("recorded", {})
            record_ids = []
            experience = recorded.get("experience")
            if isinstance(experience, dict) and experience.get("id"):
                record_ids.append(experience["id"])
            record_ids.extend(
                item["id"] for item in recorded.get("reflections", [])
                if isinstance(item, dict) and item.get("id")
            )
            capture = {
                "experience_recorded": capture_result.get("experience_recorded", False),
                "record_ids": record_ids,
                "qa": capture_result.get("qa"),
                "rejected": capture_result.get("rejected", []),
            }
            feedback = outcome.get("utility_feedback") or outcome.get("feedback")
            if isinstance(feedback, dict) and intervention:
                receipt_id = (intervention.get("receipt") or {}).get("id")
                if receipt_id and feedback.get("rating"):
                    try:
                        capture["utility_feedback"] = utility_feedback_cognition(
                            intervention_id=receipt_id,
                            rating=feedback["rating"],
                            agent_id=agent_id,
                            reason=feedback.get("reason"),
                            action=feedback.get("action"),
                            outcome=feedback.get("outcome"),
                            mute=bool(feedback.get("mute", False)),
                            applicability_correction=feedback.get("applicability_correction"),
                        )
                    except ValueError:
                        capture["utility_feedback"] = {"recorded": False}
            if capture.get("experience_recorded"):
                from memory.dreaming import run_dream
                capture["dream"] = run_dream(owner=agent_id, environment=environment)
                capture["dream_candidate_ids"] = [
                    item.get("candidate_id")
                    for item in capture["dream"].get("created", [])
                    if item.get("candidate_id")
                ]
        if event == "task_failed" and isinstance(outcome, dict):
            frontier = outcome.get("failure_frontier")
            if isinstance(frontier, dict):
                from memory.failure_frontier import record_frontier
                try:
                    capture = {
                        "frontier_recorded": record_frontier(
                            trigger=frontier.get("trigger", problem),
                            risk=frontier.get("risk", "Observed task failure."),
                            warning=frontier.get("warning", problem),
                            verification=frontier.get(
                                "verification",
                                "Reproduce the failure and run the narrowest host check.",
                            ),
                            owner=agent_id,
                            environment=environment,
                            counterexamples=frontier.get("counterexamples"),
                            source_memory_ids=frontier.get("source_memory_ids"),
                            status=frontier.get("status", "active"),
                        )
                    }
                except ValueError as error:
                    capture = {"frontier_recorded": False, "error": str(error)}
        return finish_event(
            decision,
            intervention=intervention,
            capture=capture,
            token_budget=token_budget,
        )
    except Exception as error:  # Lifecycle hooks must never block host work.
        return {
            "available": False,
            "fail_open": True,
            "event": event,
            "task_id": task_id,
            "error": str(error),
        }


def autopilot_control_cognition(action, agent_id="automation", task_id=None):
    """Pause, inspect, resume, or reversibly deprecate auto-captured records."""
    from memory.autopilot import control

    result = control(action, agent_id, task_id=task_id)
    if action != "rollback":
        return result
    rolled_back = []
    for record_id in result.pop("rollback_record_ids", []):
        try:
            update_memory_validity_cognition(
                record_id=record_id,
                state="deprecated",
                agent_id=agent_id,
                reason="Rolled back an automatic lifecycle capture.",
            )
            rolled_back.append(record_id)
        except ValueError:
            continue
    from memory.autopilot import lifecycle_events
    from memory.dreaming import rollback_candidate
    dream_rolled_back = []
    dream_ids = set()
    for event in lifecycle_events(agent_id, task_id=task_id):
        for candidate_id in (event.get("capture") or {}).get("dream_candidate_ids", []):
            if candidate_id in dream_ids:
                continue
            dream_ids.add(candidate_id)
            try:
                dream_rolled_back.append(rollback_candidate(candidate_id, owner=agent_id))
            except ValueError:
                continue
    return {
        **result,
        "rolled_back": rolled_back,
        "dream_rolled_back": dream_rolled_back,
    }


def token_ledger_cognition(agent_id="automation", task_id=None):
    from memory.autopilot import token_ledger
    return token_ledger(agent_id, task_id=task_id)


def dream_cognition(action="run", agent_id="automation", environment=None,
                    max_candidates=5, candidate_id=None, checks=None,
                    auto_promote=True):
    """Run automatic Dreaming or inspect/verify one candidate."""
    from memory.dreaming import (
        evaluate_candidate,
        list_candidates,
        rollback_candidate,
        run_dream,
    )

    if action == "run":
        return run_dream(agent_id, environment=environment, max_candidates=max_candidates)
    if action == "list":
        return {"owner": agent_id, "candidates": list_candidates(agent_id)}
    if action == "verify":
        return evaluate_candidate(
            candidate_id=candidate_id,
            checks=checks,
            owner=agent_id,
            auto_promote=auto_promote,
        )
    if action == "rollback":
        return rollback_candidate(candidate_id=candidate_id, owner=agent_id)
    raise ValueError("action must be run, list, verify, or rollback.")


def cognition_contract_cognition(contract, observations):
    """Evaluate a deterministic cognition contract without storing memory."""
    from memory.contracts import evaluate_contract
    return evaluate_contract(contract, observations)


def certify_host_cognition(host, events):
    """Check the minimum lifecycle, QA, and fail-open host contract."""
    from memory.contracts import certify_host
    return certify_host(host, events)


def compile_skill_cognition(definition, problem, environment=None):
    from memory.skill_intelligence import compile_transfer
    return compile_transfer(definition, problem, environment=environment)


def compose_skills_cognition(definitions):
    from memory.skill_intelligence import compose_skills
    return compose_skills(definitions)


def evolve_skill_cognition(definition, changes, project_id=None):
    from memory.skill_intelligence import evolve_skill
    return evolve_skill(definition, changes, project_id=project_id)


def skill_credit_cognition(
        skill_id,
        outcome,
        influence,
        agent_id="automation",
        changed_steps=None,
        warning=None):
    from memory.skill_intelligence import record_causal_credit, causal_summary
    event = record_causal_credit(
        skill_id,
        agent_id,
        outcome,
        influence,
        changed_steps=changed_steps,
        warning=warning,
    )
    return {"recorded": event, "summary": causal_summary(skill_id, agent_id)}


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


def policy_cognition(action="status", request=None):
    """Inspect or evaluate the local Memory Firewall without a provider."""
    from memory.policy import (
        evaluate_admission,
        evaluate_export,
        evaluate_retrieval,
        load_policy,
        policy_status,
        save_policy,
    )
    request = request or {}
    if action == "status":
        return policy_status(request.get("path"))
    if action == "save":
        return save_policy(request.get("policy"), request.get("path"))
    if action == "check":
        return evaluate_admission(
            files=request.get("files"),
            text=request.get("text"),
            owner=request.get("owner"),
            project_id=request.get("project_id"),
            policy=request.get("policy") or load_policy(request.get("path")),
        )
    if action == "retrieval":
        return evaluate_retrieval(
            owner=request.get("owner"),
            project_id=request.get("project_id"),
            include_shared=bool(request.get("include_shared", False)),
            policy=request.get("policy") or load_policy(request.get("path")),
        )
    if action == "export":
        return evaluate_export(
            owner=request.get("owner"),
            project_id=request.get("project_id"),
            include_shared=bool(request.get("include_shared", False)),
            approved=bool(request.get("approved", False)),
            policy=request.get("policy") or load_policy(request.get("path")),
        )
    raise ValueError("policy action must be status, save, check, retrieval, or export.")


def capsule_cognition(action, request=None):
    """Create, verify, inspect, or import a portable cognition capsule."""
    from memory.capsule import capsule_action
    return capsule_action(action, request or {})


def replay_cognition(action, request=None):
    """Compare captured cognition conditions deterministically."""
    from memory.replay import replay_action
    return replay_action(action, request or {})


def doctor_cognition():
    """Return local service, policy, journal, and storage diagnostics."""
    from memory.service import doctor
    return doctor()


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
        human_approved=False,
        **contract):
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
        **contract,
    )
