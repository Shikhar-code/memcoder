"""Provider-free MCP interface for MemCoder cognition."""

import json

from fastmcp import FastMCP

from memory.markdown_import import import_markdown, import_markdown_file
from api.cognition import prepare_cognition, record_cognition


mcp = FastMCP("memcoder")


@mcp.tool()
def memcoder_prepare(
        problem: str,
        agent_id: str = "antigravity",
        include_shared: bool = True,
        include_knowledge: bool = True,
        subject: str | None = None,
        category: str | None = None) -> str:
    """Retrieve provider-independent cognition before the host agent solves."""

    return json.dumps(
        prepare_cognition(
            problem,
            agent_id=agent_id,
            include_shared=include_shared,
            include_knowledge=include_knowledge,
            subject=subject,
            category=category,
        ),
        indent=2
    )


@mcp.tool()
def memcoder_record(
        task: str,
        files: list[str],
        summary: str,
        solution: str,
        reflection: str | None = None,
        principles: list[str] | None = None,
        agent_id: str = "antigravity") -> str:
    """Record a structured outcome supplied by the host agent after a fix."""

    recorded = record_cognition(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
        reflection=reflection,
        principles=principles,
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
