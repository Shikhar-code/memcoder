"""Admission checks for automatically extracted memories."""

import re


PLACEHOLDERS = {
    "",
    "...",
    "unknown",
    "none",
    "n/a",
    "na",
    "not available",
    "describe the problem",
    "identify a coding experience from the conversation",
}

BAD_FILES = {
    "",
    "...",
    "unknown",
    "response.py",
    "ollama.chat()",
    "thinking",
    "content",
}

REFLECTION_PROCESS_WORDS = {
    "assumed", "checked", "confirmed", "debugged", "inspected",
    "investigated", "misread", "overlooked", "reproduced", "rushed",
    "tested", "traced", "verified"
}

REFLECTION_SOLUTION_WORDS = {
    "added", "changed", "created", "fixed", "implemented", "updated",
    "wrote"
}


def is_meaningful_text(value, minimum_words=1):
    if value is None:
        return False

    text = str(value).strip()

    if text.lower() in PLACEHOLDERS:
        return False

    return len(text.split()) >= minimum_words


def has_usable_files(files):
    if not isinstance(files, list):
        return False

    return any(
        str(file).strip().lower() not in BAD_FILES
        for file in files
    )


def is_valid_experience(memory):
    if not isinstance(memory, dict):
        return False

    return (
        is_meaningful_text(memory.get("task"))
        and is_meaningful_text(memory.get("summary"), minimum_words=3)
        and is_meaningful_text(memory.get("solution"), minimum_words=3)
        and has_usable_files(memory.get("files"))
    )


def is_valid_reflection(reflection):
    if not is_meaningful_text(reflection, minimum_words=3):
        return False

    text = str(reflection).strip()
    word_count = len(text.split())

    words = set(re.findall(r"[a-z]+", text.lower()))

    return (
        text.startswith("I ")
        and word_count <= 20
        and len(re.findall(r"[.!?]", text)) <= 1
        and bool(words & REFLECTION_PROCESS_WORDS)
        and not bool(words & REFLECTION_SOLUTION_WORDS)
        and not bool(words & {"should", "always", "never"})
    )


def is_valid_principle(principle):
    return is_meaningful_text(
        principle,
        minimum_words=3
    )
