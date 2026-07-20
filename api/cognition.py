"""Provider-free cognition operations shared by MCP and automation hosts."""

def compact_memory(memory):
    """Return the stable, serializable memory shape exposed to hosts."""
    return {
        "task": memory.get("task", ""),
        "summary": memory.get("summary", ""),
        "solution": memory.get("solution", ""),
        "files": memory.get("files", []),
        "distance": memory.get("score"),
        "confidence": memory.get("retrieval_confidence"),
        "source": memory.get("source", "")
    }


def compact_knowledge(knowledge):
    """Return source-traceable reference knowledge without treating it as memory."""
    return {
        "content": knowledge.get("content", ""),
        "subject": knowledge.get("subject", ""),
        "category": knowledge.get("category", ""),
        "document": knowledge.get("document", ""),
        "section": knowledge.get("section", ""),
        "source_path": knowledge.get("source_path", ""),
        "source_hash": knowledge.get("source_hash", ""),
        "distance": knowledge.get("distance"),
        "confidence": knowledge.get("confidence"),
    }


def prepare_cognition(
        problem,
        agent_id="automation",
        include_shared=True,
        include_knowledge=True,
        subject=None,
        category=None):
    """Retrieve trusted guidance before an independent host starts work."""
    from memory.hierarchical_search import hierarchical_search

    results = hierarchical_search(
        problem,
        agent_id=agent_id,
        include_shared=include_shared
    )

    knowledge = []
    if include_knowledge:
        from memory.knowledge import search_knowledge
        knowledge = search_knowledge(
            problem,
            subject=subject,
            category=category,
        )

    return {
        "problem": problem,
        "include_shared": include_shared,
        "knowledge": [
            compact_knowledge(item)
            for item in knowledge
        ],
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
            "Use retrieved knowledge as source-traceable prerequisite context.",
            "Prefer listed files and verification steps before broad exploration.",
            "If no trusted memory is present, solve normally.",
            "Record an outcome only after the host has verified success."
        ]
    }


def record_cognition(
        task,
        files,
        summary,
        solution,
        reflection=None,
        principles=None,
        agent_id="automation"):
    """Persist a structured outcome supplied by a host after verification."""
    from memory.record_outcome import record_outcome

    recorded = record_outcome(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
        reflection=reflection,
        principles=principles,
        agent_id=agent_id
    )

    return {
        "recorded": recorded,
        "experience_recorded": recorded["experience"] is not None,
        "rejected": recorded.get("rejected", [])
    }
