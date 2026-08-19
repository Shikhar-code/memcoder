"""Provider-free MCP interface for MemCoder cognition."""

import json

from fastmcp import FastMCP

from memory.markdown_import import import_markdown, import_markdown_file
from api.cognition import (
    autopilot_control_cognition,
    autopilot_event_cognition,
    certify_host_cognition,
    host_manifest_cognition,
    checkpoint_cognition,
    compile_skill_cognition,
    compose_skills_cognition,
    cognition_contract_cognition,
    cognitive_branch_cognition,
    dream_cognition,
    intervene_cognition,
    project_accept_cognition,
    project_handoff_cognition,
    project_resurrect_cognition,
    project_update_cognition,
    retrieval_debug_cognition,
    plan_cognition,
    plan_history_cognition,
    policy_cognition,
    capsule_cognition,
    replay_cognition,
    doctor_cognition,
    retention_preview_cognition,
    apply_retention_cognition,
    report_contradiction_cognition,
    resolve_contradiction_cognition,
    trace_memory_cognition,
    evaluate_cognition,
    evolve_skill_cognition,
    failure_frontier_cognition,
    prepare_cognition,
    promote_skill_cognition,
    record_cognition,
    skill_health_cognition,
    skill_credit_cognition,
    start_cognition,
    task_state_cognition,
    token_ledger_cognition,
    update_memory_validity_cognition,
    utility_feedback_cognition,
    utility_feedback_summary_cognition,
    verify_cognition,
)


mcp = FastMCP("memcoder")


@mcp.tool()
def memcoder_autopilot(
        event: str,
        task_id: str,
        problem: str,
        agent_id: str = "codex",
        include_shared: bool = True,
        environment: dict | None = None,
        context: dict | None = None,
        action: str | None = None,
        outcome: dict | None = None,
        token_budget: int = 450,
        host: str = "codex") -> str:
    """Handle one host lifecycle boundary and close explicit outcomes; fail open."""
    return json.dumps(autopilot_event_cognition(
        event=event,
        task_id=task_id,
        problem=problem,
        agent_id=agent_id,
        include_shared=include_shared,
        environment=environment,
        context=context,
        action=action,
        outcome=outcome,
        token_budget=token_budget,
        host=host,
    ), indent=2)


@mcp.tool()
def memcoder_autopilot_control(
        action: str,
        agent_id: str = "codex",
        task_id: str | None = None) -> str:
    """Pause, resume, inspect, or roll back automatic cognition."""
    return json.dumps(autopilot_control_cognition(action, agent_id, task_id), indent=2)


@mcp.tool()
def memcoder_token_ledger(agent_id: str = "codex", task_id: str | None = None) -> str:
    """Inspect measured lifecycle cognition token accounting."""
    return json.dumps(token_ledger_cognition(agent_id, task_id), indent=2)


@mcp.tool()
def memcoder_dream(
        action: str = "run",
        agent_id: str = "codex",
        environment: dict | None = None,
        max_candidates: int = 5,
        candidate_id: str | None = None,
        checks: list[dict] | None = None,
        auto_promote: bool = True) -> str:
    """Run automatic local Dreaming or verify one candidate for promotion."""
    return json.dumps(dream_cognition(
        action=action,
        agent_id=agent_id,
        environment=environment,
        max_candidates=max_candidates,
        candidate_id=candidate_id,
        checks=checks,
        auto_promote=auto_promote,
    ), indent=2)


@mcp.tool()
def memcoder_cognition_contract(contract: dict, observations: dict) -> str:
    """Evaluate a deterministic cognition contract without storing memory."""
    return json.dumps(cognition_contract_cognition(contract, observations), indent=2)


@mcp.tool()
def memcoder_host_manifest(host: str) -> str:
    """Return the provider-free lifecycle contract for a supported host."""
    return json.dumps(host_manifest_cognition(host), indent=2)


@mcp.tool()
def memcoder_host_certify(
        host: str,
        events: list[dict],
        strict: bool = False) -> str:
    """Certify a host's lifecycle, QA, privacy, and optional strict receipts."""
    return json.dumps(certify_host_cognition(host, events, strict=strict), indent=2)


@mcp.tool()
def memcoder_compile_skill(
        definition: dict,
        problem: str,
        environment: dict | None = None) -> str:
    """Compile reusable and adaptation steps for safe current-context transfer."""
    return json.dumps(compile_skill_cognition(definition, problem, environment), indent=2)


@mcp.tool()
def memcoder_compose_skills(definitions: list[dict]) -> str:
    """Compose compatible skills and refuse conflicting mutations."""
    return json.dumps(compose_skills_cognition(definitions), indent=2)


@mcp.tool()
def memcoder_evolve_skill(
        definition: dict,
        changes: dict,
        project_id: str | None = None) -> str:
    """Create a reviewable next skill version without overwriting history."""
    return json.dumps(evolve_skill_cognition(definition, changes, project_id), indent=2)


@mcp.tool()
def memcoder_skill_credit(
        skill_id: str,
        outcome: str,
        influence: str,
        agent_id: str = "codex",
        changed_steps: list[str] | None = None,
        warning: str | None = None) -> str:
    """Record causal skill influence separately from mere presence."""
    return json.dumps(skill_credit_cognition(
        skill_id, outcome, influence, agent_id, changed_steps, warning
    ), indent=2)


@mcp.tool()
def memcoder_intervene(
        problem: str,
        agent_id: str = "codex",
        include_shared: bool = True,
        environment: dict | None = None,
        token_budget: int = 450) -> str:
    """Return the smallest useful cognition packet for the current task."""

    return json.dumps(
        intervene_cognition(
            problem=problem,
            agent_id=agent_id,
            include_shared=include_shared,
            environment=environment,
            token_budget=token_budget,
        ),
        indent=2,
    )


@mcp.tool()
def memcoder_utility_feedback(
        intervention_id: str,
        rating: str,
        agent_id: str = "codex",
        reason: str | None = None,
        action: str | None = None,
        outcome: str | None = None,
        mute: bool = False,
        applicability_correction: dict | None = None) -> str:
    """Rate one exact intervention as helpful, ignored, misleading, or harmful."""

    return json.dumps(utility_feedback_cognition(
        intervention_id=intervention_id,
        rating=rating,
        agent_id=agent_id,
        reason=reason,
        action=action,
        outcome=outcome,
        mute=mute,
        applicability_correction=applicability_correction,
    ), indent=2)


@mcp.tool()
def memcoder_utility_summary(
        memory_id: str | None = None,
        agent_id: str = "codex",
        environment: dict | None = None) -> str:
    """Summarize observed intervention outcomes for calibration without mutating memory."""
    return json.dumps(utility_feedback_summary_cognition(
        memory_id=memory_id, agent_id=agent_id, environment=environment
    ), indent=2)


@mcp.tool()
def memcoder_failure_frontier(
        action: str = "match",
        problem: str | None = None,
        trigger: str | None = None,
        risk: str | None = None,
        warning: str | None = None,
        verification: str | None = None,
        owner: str = "codex",
        environment: dict | None = None,
        counterexamples: list[str] | None = None,
        source_memory_ids: list[str] | None = None,
        frontier_id: str | None = None,
        status: str | None = None,
        outcome: str | None = None,
        reason: str | None = None,
        limit: int = 5) -> str:
    """Record or retrieve append-only, evidence-backed failure warnings."""
    return json.dumps(failure_frontier_cognition(
        action=action, problem=problem, trigger=trigger, risk=risk,
        warning=warning, verification=verification, owner=owner,
        environment=environment, counterexamples=counterexamples,
        source_memory_ids=source_memory_ids, frontier_id=frontier_id,
        status=status, outcome=outcome, reason=reason, limit=limit,
    ), indent=2)


@mcp.tool()
def memcoder_cognitive_branch(
        action: str = "list",
        branch_id: str | None = None,
        target_branch_id: str | None = None,
        name: str | None = None,
        owner: str = "codex",
        project_id: str | None = None,
        environment: dict | None = None,
        base_environment: dict | None = None,
        base_ref: str | None = None,
        kind: str | None = None,
        key: str | None = None,
        before=None,
        after=None,
        memory_ids: list[str] | None = None,
        obligation_id: str | None = None,
        obligation_name: str | None = None,
        obligation_kind: str = "test",
        command: str | None = None,
        passed: bool | None = None,
        evidence=None,
        apply: bool = False,
        reason: str | None = None,
        status: str | None = None) -> str:
    """Create, diff, prove, merge, or roll back branch-local cognition."""
    return json.dumps(cognitive_branch_cognition(
        action=action, branch_id=branch_id, target_branch_id=target_branch_id,
        name=name, owner=owner, project_id=project_id, environment=environment,
        base_environment=base_environment, base_ref=base_ref, kind=kind,
        key=key, before=before, after=after, memory_ids=memory_ids,
        obligation_id=obligation_id, obligation_name=obligation_name,
        obligation_kind=obligation_kind, command=command, passed=passed,
        evidence=evidence, apply=apply, reason=reason, status=status,
    ), indent=2)


@mcp.tool()
def memcoder_retrieval_debug(
        problem: str,
        agent_id: str = "codex",
        include_shared: bool = True,
        environment: dict | None = None,
        utility_threshold: float | None = None) -> str:
    """Explain semantic rank, utility rank, gates, and withheld guidance."""

    return json.dumps(retrieval_debug_cognition(
        problem=problem,
        agent_id=agent_id,
        include_shared=include_shared,
        environment=environment,
        utility_threshold=utility_threshold,
    ), indent=2)


@mcp.tool()
def memcoder_checkpoint(
        task_id: str,
        update: dict,
        agent_id: str = "codex",
        prediction_result: dict | None = None) -> str:
    """Save bounded task state without creating semantic memory."""

    return json.dumps(
        checkpoint_cognition(
            task_id=task_id,
            update=update,
            agent_id=agent_id,
            prediction_result=prediction_result,
        ),
        indent=2,
    )


@mcp.tool()
def memcoder_task_state(task_id: str, agent_id: str = "codex") -> str:
    """Read the latest owner-scoped task checkpoint."""

    return json.dumps(
        task_state_cognition(task_id=task_id, agent_id=agent_id), indent=2
    )


@mcp.tool()
def memcoder_project_update(
        project_id: str,
        update: dict,
        agent_id: str = "codex",
        environment: dict | None = None) -> str:
    """Incrementally store bounded project facts, risks, goals, and decisions."""

    return json.dumps(project_update_cognition(
        project_id=project_id,
        update=update,
        agent_id=agent_id,
        environment=environment,
    ), indent=2)


@mcp.tool()
def memcoder_project_resurrect(
        project_id: str,
        agent_id: str = "codex",
        environment: dict | None = None,
        token_budget: int = 600) -> str:
    """Recover a bounded continuation brief with stale decisions withheld."""

    return json.dumps(project_resurrect_cognition(
        project_id=project_id,
        agent_id=agent_id,
        environment=environment,
        token_budget=token_budget,
    ), indent=2)


@mcp.tool()
def memcoder_project_handoff(
        project_id: str,
        agent_id: str = "codex",
        environment: dict | None = None) -> str:
    """Export a bounded, secret-scrubbed project cognition capsule."""

    return json.dumps(project_handoff_cognition(
        project_id=project_id,
        agent_id=agent_id,
        environment=environment,
    ), indent=2)


@mcp.tool()
def memcoder_project_accept(
        capsule: dict,
        agent_id: str = "codex",
        environment: dict | None = None) -> str:
    """Accept a project handoff and report receiver environment drift."""

    return json.dumps(project_accept_cognition(
        capsule=capsule,
        agent_id=agent_id,
        environment=environment,
    ), indent=2)


@mcp.tool()
def memcoder_start(
        problem: str,
        agent_id: str = "antigravity",
        include_shared: bool = True,
        environment: dict | None = None) -> str:
    """Start a task: return compact guidance and a bounded plan in one call."""

    options = {"problem": problem, "agent_id": agent_id, "include_shared": include_shared}
    if environment is not None:
        options["environment"] = environment
    return json.dumps(start_cognition(**options), indent=2)


@mcp.tool()
def memcoder_prepare(
        problem: str,
        agent_id: str = "antigravity",
        include_shared: bool = True,
        include_skills: bool = True,
        detail_level: str = "brief",
        environment: dict | None = None) -> str:
    """Retrieve provider-independent cognition before the host agent solves."""

    options = {
        "agent_id": agent_id,
        "include_shared": include_shared,
        "include_skills": include_skills,
        "detail_level": detail_level,
    }
    if environment is not None:
        options["environment"] = environment
    return json.dumps(prepare_cognition(problem, **options), indent=2)


@mcp.tool()
def memcoder_plan(
        problem: str,
        agent_id: str = "antigravity",
        include_shared: bool = True,
        environment: dict | None = None) -> str:
    """Build a bounded plan from retrieved QA-backed skills when available."""

    options = {"problem": problem, "agent_id": agent_id, "include_shared": include_shared}
    if environment is not None:
        options["environment"] = environment
    return json.dumps(plan_cognition(**options), indent=2)


@mcp.tool()
def memcoder_plan_history(
        plan_id: str,
        agent_id: str = "antigravity") -> str:
    """Read the owner-scoped audit history for a MemCoder plan."""

    return json.dumps(
        plan_history_cognition(plan_id=plan_id, agent_id=agent_id),
        indent=2
    )


@mcp.tool()
def memcoder_skill_health(
        skill_id: str,
        agent_id: str = "antigravity") -> str:
    """Read whether a Skill is trusted, monitored, unproven, or needs review."""

    return json.dumps(
        skill_health_cognition(skill_id=skill_id, agent_id=agent_id),
        indent=2
    )


@mcp.tool()
def memcoder_update_validity(
        record_id: str,
        state: str,
        agent_id: str = "antigravity",
        reason: str | None = None,
        environment: dict | None = None) -> str:
    """Mark a memory trusted, superseded, contradicted, or deprecated."""

    return json.dumps(
        update_memory_validity_cognition(
            record_id=record_id,
            state=state,
            agent_id=agent_id,
            reason=reason,
            environment=environment,
        ),
        indent=2,
    )


@mcp.tool()
def memcoder_retention_preview(
        agent_id: str | None = None,
        environment: dict | None = None) -> str:
    """Preview safe exact-duplicate retention actions without changing memory."""

    return json.dumps(
        retention_preview_cognition(agent_id=agent_id, environment=environment), indent=2
    )


@mcp.tool()
def memcoder_retention_apply(preview: dict, agent_id: str | None = None) -> str:
    """Apply an explicitly supplied retention preview without deleting evidence."""

    return json.dumps(
        apply_retention_cognition(preview=preview, agent_id=agent_id), indent=2
    )


@mcp.tool()
def memcoder_trace_memory(record_id: str, agent_id: str = "antigravity") -> str:
    """Inspect one memory's current state and direct provenance evidence."""

    return json.dumps(trace_memory_cognition(record_id, agent_id=agent_id), indent=2)


@mcp.tool()
def memcoder_report_contradiction(
        first_id: str,
        second_id: str,
        reason: str,
        agent_id: str = "antigravity") -> str:
    """Withhold two conflicting memories from automatic reuse without deleting them."""

    return json.dumps(
        report_contradiction_cognition(first_id, second_id, reason, agent_id=agent_id),
        indent=2,
    )


@mcp.tool()
def memcoder_resolve_contradiction(
        winner_id: str,
        loser_id: str,
        reason: str,
        agent_id: str = "antigravity") -> str:
    """Restore a reviewed winner and supersede the conflicting alternative."""

    return json.dumps(
        resolve_contradiction_cognition(winner_id, loser_id, reason, agent_id=agent_id),
        indent=2,
    )


@mcp.tool()
def memcoder_evaluate(runs: list[dict]) -> str:
    """Summarize host-supplied baseline and MemCoder-assisted evaluation runs."""

    return json.dumps(evaluate_cognition(runs), indent=2)


@mcp.tool()
def memcoder_promote_skill(
        name: str,
        when_to_use: str,
        inputs: list[str],
        steps: list[str],
        verification: list[str],
        supporting_experience_ids: list[str],
        supporting_principle_ids: list[str] | None = None,
        agent_id: str = "antigravity",
        human_approved: bool = False,
        purpose: str | None = None,
        preconditions: list[str] | None = None,
        decision_points: list[str] | None = None,
        expected_observations: list[str] | None = None,
        failure_handling: list[str] | None = None,
        rollback: list[str] | None = None,
        applicability_limits: list[str] | None = None,
        state_mutations: list[str] | None = None,
        resources: list[str] | None = None) -> str:
    """Promote one skill from QA-approved supporting experiences only."""

    return json.dumps(
        promote_skill_cognition(
            name=name,
            when_to_use=when_to_use,
            inputs=inputs,
            steps=steps,
            verification=verification,
            supporting_experience_ids=supporting_experience_ids,
            supporting_principle_ids=supporting_principle_ids,
            agent_id=agent_id,
            human_approved=human_approved,
            purpose=purpose,
            preconditions=preconditions,
            decision_points=decision_points,
            expected_observations=expected_observations,
            failure_handling=failure_handling,
            rollback=rollback,
            applicability_limits=applicability_limits,
            state_mutations=state_mutations,
            resources=resources,
        ),
        indent=2
    )


@mcp.tool()
def memcoder_verify(
        task: str,
        files: list[str],
        summary: str,
        solution: str,
        evidence: dict,
        reflection: str | None = None,
        principles: list[str] | None = None) -> str:
    """QA host-supplied evidence without storing any outcome or memory."""

    return json.dumps(
        verify_cognition(
            task=task,
            files=files,
            summary=summary,
            solution=solution,
            evidence=evidence,
            reflection=reflection,
            principles=principles,
        ),
        indent=2
    )


@mcp.tool()
def memcoder_record(
        task: str,
        files: list[str],
        summary: str,
        solution: str,
        evidence: dict,
        reflection: str | None = None,
        principles: list[str] | None = None,
        plan_id: str | None = None,
        applied_skill_id: str | None = None,
        agent_id: str = "antigravity",
        environment: dict | None = None) -> str:
    """QA and record a structured outcome only when evidence is sufficient."""

    options = dict(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
            evidence=evidence,
            reflection=reflection,
            principles=principles,
            plan_id=plan_id,
        applied_skill_id=applied_skill_id,
        agent_id=agent_id,
    )
    if environment is not None:
        options["environment"] = environment
    recorded = record_cognition(**options)

    return json.dumps(recorded, indent=2)


@mcp.tool()
def memcoder_policy(action: str = "status", request: dict | None = None) -> str:
    """Inspect or evaluate local admission, retrieval, and export policy."""
    return json.dumps(policy_cognition(action=action, request=request or {}), indent=2)


@mcp.tool()
def memcoder_replay(action: str = "compare", request: dict | None = None) -> str:
    """Compare or retrieve deterministic baseline-versus-memory receipts."""
    return json.dumps(replay_cognition(action=action, request=request or {}), indent=2)


@mcp.tool()
def memcoder_capsule(action: str = "inspect", request: dict | None = None) -> str:
    """Export, verify, inspect, or dry-run import a checksummed cognition capsule."""
    return json.dumps(capsule_cognition(action=action, request=request or {}), indent=2)


@mcp.tool()
def memcoder_doctor() -> str:
    """Return provider-free local storage, policy, and journal diagnostics."""
    return json.dumps(doctor_cognition(), indent=2)


@mcp.tool()
def memcoder_import_markdown(
        markdown: str,
        source_name: str,
        agent_id: str = "antigravity",
        approve: bool = False) -> str:
    """Preview Markdown guidance; call again with approve=true to store it."""

    result = import_markdown(
        markdown=markdown,
        source_name=source_name,
        agent_id=agent_id,
        approve=approve
    )

    return json.dumps(result, indent=2)


@mcp.tool()
def memcoder_import_markdown_file(
        file_path: str,
        agent_id: str = "antigravity",
        approve: bool = False) -> str:
    """Preview a project Markdown file; call again with approve=true to store it.

    The file must be a UTF-8 .md/.markdown file inside the current project
    directory. This tool never imports experiences or reflections.
    """

    result = import_markdown_file(
        file_path=file_path,
        agent_id=agent_id,
        approve=approve
    )

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    from memory.embedder import prewarm_async
    prewarm_async()
    mcp.run(show_banner=False)
