"""Provider-free MCP interface for MemCoder cognition."""

import json

from fastmcp import FastMCP

from memory.markdown_import import import_markdown, import_markdown_file
from api.cognition import (
    plan_cognition,
    plan_history_cognition,
    retention_preview_cognition,
    apply_retention_cognition,
    report_contradiction_cognition,
    resolve_contradiction_cognition,
    trace_memory_cognition,
    evaluate_cognition,
    prepare_cognition,
    promote_skill_cognition,
    record_cognition,
    skill_health_cognition,
    start_cognition,
    update_memory_validity_cognition,
    verify_cognition,
)


mcp = FastMCP("memcoder")


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
        human_approved: bool = False) -> str:
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
    mcp.run()
