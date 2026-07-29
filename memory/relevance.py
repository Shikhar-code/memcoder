"""Shared ranking and trust policy for vector-search candidates."""

import re

from memory.validity import retrieval_eligible


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


def verification_strength(memory):
    """Reward guidance that carries a concrete current-task proof path."""
    proof = memory.get("proof") if isinstance(memory.get("proof"), dict) else {}
    required = proof.get("required_verification", [])
    if isinstance(required, list) and required:
        if any(str(item).startswith(("Run:", "Confirm:", "Repeat:")) for item in required):
            return 0.10
        return 0.05
    return 0.0


def rank_memories(memories, query="", current_environment=None):
    ranked = []

    for memory in memories:
        ranked_memory = dict(memory)
        confidence = memory_confidence(ranked_memory)
        overlap = lexical_overlap(ranked_memory, query)
        eligible, applicability = retrieval_eligible(
            ranked_memory,
            current_environment=current_environment,
        )

        ranked_memory["retrieval_confidence"] = round(confidence, 2)
        ranked_memory["lexical_overlap"] = overlap
        ranked_memory["verification_strength"] = verification_strength(ranked_memory)
        ranked_memory["relevance_score"] = round(
            confidence + min(overlap, 3) * 0.05
            + ranked_memory["verification_strength"] - applicability["penalty"],
            2
        )
        ranked_memory["applicability"] = applicability["status"]
        ranked_memory["automatic_retrieval_allowed"] = eligible

        ranked.append(ranked_memory)

    return sorted(
        ranked,
        key=lambda memory: memory["relevance_score"],
        reverse=True
    )


def is_trusted_memory(memory, query="", current_environment=None):
    eligible, _ = retrieval_eligible(memory, current_environment=current_environment)
    if not eligible:
        return False
    confidence = memory_confidence(memory)

    if confidence >= HIGH_MEMORY_CONFIDENCE:
        return True

    return (
        confidence >= MIN_MEMORY_CONFIDENCE
        and lexical_overlap(memory, query) > 0
    )


def filter_trusted_memories(
        memories,
        query="",
        current_environment=None):
    """Keep high-confidence candidates and grounded mid-confidence matches."""

    return [
        memory
        for memory in rank_memories(memories, query, current_environment=current_environment)
        if is_trusted_memory(memory, query, current_environment=current_environment)
    ]
