"""Provider-free MCP interface for MemCoder cognition."""

import json

from fastmcp import FastMCP

from memory.hierarchical_search import hierarchical_search
from memory.record_outcome import record_outcome
from memory.markdown_import import import_markdown, import_markdown_file


mcp = FastMCP("memcoder")


def compact_memory(memory):
    return {
        "task": memory.get("task", ""),
        "summary": memory.get("summary", ""),
        "solution": memory.get("solution", ""),
        "files": memory.get("files", []),
        "distance": memory.get("score"),
        "confidence": memory.get("retrieval_confidence"),
        "source": memory.get("source", "")
    }


def prepare_cognition(
        problem,
        agent_id="antigravity",
        include_shared=True):
    results = hierarchical_search(
        problem,
        agent_id=agent_id,
        include_shared=include_shared
    )

    return {
        "problem": problem,
        "include_shared": include_shared,
        "confidence": results["confidence"],
        "strategy": results["strategy"],
        "experiences": [
            compact_memory(memory)
            for memory in results["experiences"]
        ],
        "mistakes": [
            compact_memory(memory)
            for memory in results["mistakes"]
        ],
        "principles": [
            compact_memory(memory)
            for memory in results["principles"]
        ],
        "reflections": [
            compact_memory(memory)
            for memory in results["reflections"]
        ],
        "instructions": [
            "Use trusted memories as investigation guidance, not proof.",
            "Prefer listed files and verification steps before broad exploration.",
            "If no trusted memory is present, solve normally.",
            "After a successful fix, call memcoder_record with a structured outcome."
        ]
    }


@mcp.tool()
def memcoder_prepare(
        problem: str,
        agent_id: str = "antigravity",
        include_shared: bool = True) -> str:
    """Retrieve provider-independent cognition before the host agent solves."""

    return json.dumps(
        prepare_cognition(
            problem,
            agent_id=agent_id,
            include_shared=include_shared
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

    recorded = record_outcome(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
        reflection=reflection,
        principles=principles,
        agent_id=agent_id
    )

    return json.dumps(
        {
            "recorded": recorded,
            "experience_recorded": recorded["experience"] is not None,
            "rejected": recorded.get("rejected", [])
        },
        indent=2
    )


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
