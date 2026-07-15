"""Shared ranking and trust policy for vector-search candidates."""

import re


MIN_MEMORY_CONFIDENCE = 0.60
HIGH_MEMORY_CONFIDENCE = 0.75

STOP_WORDS = {
    "a", "an", "and", "are", "at", "be", "by", "does", "for",
    "from", "in", "into", "is", "it", "its", "of", "on", "or",
    "the", "this", "that", "to", "was", "when", "with", "without"
}


def memory_confidence(memory):
    """Convert Chroma's squared-L2 distance for unit vectors to similarity."""

    try:
        distance = float(memory["score"])
    except (KeyError, TypeError, ValueError):
        return 0.0

    # For normalized embeddings: squared L2 distance = 2 * (1 - cosine).
    return max(0.0, min(1.0, 1.0 - (distance / 2.0)))


def query_terms(text):
    return {
        term
        for term in re.findall(r"[a-z0-9_]+", text.lower())
        if len(term) > 2 and term not in STOP_WORDS
    }


def memory_text(memory):
    fields = [
        memory.get("task", ""),
        memory.get("summary", ""),
        memory.get("solution", ""),
        " ".join(memory.get("files", []))
    ]

    return " ".join(
        str(field)
        for field in fields
    )


def lexical_overlap(memory, query):
    if not query:
        return 0

    return len(
        query_terms(query)
        & query_terms(memory_text(memory))
    )


def rank_memories(memories, query=""):
    ranked = []

    for memory in memories:
        ranked_memory = dict(memory)
        confidence = memory_confidence(ranked_memory)
        overlap = lexical_overlap(ranked_memory, query)

        ranked_memory["retrieval_confidence"] = round(confidence, 2)
        ranked_memory["lexical_overlap"] = overlap
        ranked_memory["relevance_score"] = round(
            confidence + min(overlap, 3) * 0.05,
            2
        )

        ranked.append(ranked_memory)

    return sorted(
        ranked,
        key=lambda memory: memory["relevance_score"],
        reverse=True
    )


def is_trusted_memory(memory, query=""):
    confidence = memory_confidence(memory)

    if confidence >= HIGH_MEMORY_CONFIDENCE:
        return True

    return (
        confidence >= MIN_MEMORY_CONFIDENCE
        and lexical_overlap(memory, query) > 0
    )


def filter_trusted_memories(
        memories,
        query=""):
    """Keep high-confidence candidates and grounded mid-confidence matches."""

    return [
        memory
        for memory in rank_memories(memories, query)
        if is_trusted_memory(memory, query)
    ]
