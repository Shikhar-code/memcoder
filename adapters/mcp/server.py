"""Provider-free MCP interface for MemCoder cognition."""

import json

from fastmcp import FastMCP

from memory.markdown_import import import_markdown, import_markdown_file
from api.cognition import (
    plan_cognition,
    plan_history_cognition,
    evaluate_cognition,
    prepare_cognition,
    promote_skill_cognition,
    record_cognition,
    skill_health_cognition,
    start_cognition,
    verify_cognition,
)


mcp = FastMCP("memcoder")


@mcp.tool()
def memcoder_start(
        problem: str,
        agent_id: str = "antigravity",
        include_shared: bool = True) -> str:
    """Start a task: return compact guidance and a bounded plan in one call."""

    return json.dumps(
        start_cognition(
            problem=problem,
            agent_id=agent_id,
            include_shared=include_shared,
        ),
        indent=2
    )


@mcp.tool()
def memcoder_prepare(
        problem: str,
        agent_id: str = "antigravity",
        include_shared: bool = True,
        include_skills: bool = True,
        detail_level: str = "brief") -> str:
    """Retrieve provider-independent cognition before the host agent solves."""

    return json.dumps(
        prepare_cognition(
            problem,
            agent_id=agent_id,
            include_shared=include_shared,
            include_skills=include_skills,
            detail_level=detail_level,
        ),
        indent=2
    )


@mcp.tool()
def memcoder_plan(
        problem: str,
        agent_id: str = "antigravity",
        include_shared: bool = True) -> str:
    """Build a bounded plan from retrieved QA-backed skills when available."""

    return json.dumps(
        plan_cognition(
            problem=problem,
            agent_id=agent_id,
            include_shared=include_shared,
        ),
        indent=2
    )


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
        agent_id: str = "antigravity") -> str:
    """QA and record a structured outcome only when evidence is sufficient."""

    recorded = record_cognition(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
            evidence=evidence,
            reflection=reflection,
            principles=principles,
            plan_id=plan_id,
            applied_skill_id=applied_skill_id,
        agent_id=agent_id
    )

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
