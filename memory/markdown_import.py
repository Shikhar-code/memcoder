"""Deterministic, approval-gated Markdown bootstrap for project guidance."""

import re
from pathlib import Path

from memory.principle_capture import capture_principles
from memory.quality import is_valid_principle


MAX_CANDIDATES = 50
MAX_MARKDOWN_BYTES = 1_000_000
UNSAFE_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "reveal the system prompt",
    "exfiltrate",
    "bypass safety",
    "disable safety"
)
ACTIONABLE_STARTS = (
    "always ", "never ", "do not ", "don't ", "avoid ", "prefer ",
    "use ", "keep ", "validate ", "run ", "test ", "verify ",
    "check ", "ensure ", "record ", "call ", "add ", "remove ",
    "write ", "read ", "treat ", "limit ", "only ", "before ",
    "after ", "when ", "if ", "all ", "every ", "no "
)
ACTIONABLE_MARKERS = (
    " must ", " should ", " required ", "require ", "need to ",
    "do not ", "don't ", "never "
)


def clean_markdown_item(text):
    """Keep readable content while removing simple Markdown markers."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`]+", "", text)
    return " ".join(text.split()).strip()


def is_actionable_guidance(principle):
    """Accept instructions and policies, not factual product descriptions."""
    text = principle.lower().strip()
    padded = f" {text} "
    return (
        text.startswith(ACTIONABLE_STARTS)
        or any(marker in padded for marker in ACTIONABLE_MARKERS)
    )


def preview_markdown_import(markdown, source_name):
    """Extract safe actionable bullet-point guidance without persistence."""
    if not isinstance(markdown, str) or not markdown.strip():
        return {
            "source_name": source_name,
            "candidates": [],
            "rejected": ["Markdown content is empty."]
        }

    source_name = str(source_name).strip() or "Markdown document"
    candidates = []
    rejected = []
    seen = set()
    in_code_block = False
    section = ""
    current_item = None

    def add_item(raw_item):
        if raw_item is None:
            return

        principle = clean_markdown_item(raw_item)
        key = principle.lower()

        if not is_valid_principle(principle):
            rejected.append(
                f"Skipped a short or placeholder item: {principle or 'empty'}"
            )
        elif any(pattern in key for pattern in UNSAFE_PATTERNS):
            rejected.append(f"Skipped unsafe instruction: {principle}")
        elif not is_actionable_guidance(principle):
            rejected.append(f"Skipped non-instructional item: {principle}")
        elif key not in seen:
            seen.add(key)
            candidates.append({
                "type": "principle",
                "task": principle,
                "summary": (
                    f"Imported from {source_name}"
                    + (f" - {section}" if section else "")
                ),
                "source": source_name
            })

    for raw_line in markdown.splitlines():
        line = raw_line.strip()

        if line.startswith("```"):
            add_item(current_item)
            current_item = None
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        heading = re.match(r"^#{1,6}\s+(.+)$", line)
        if heading:
            add_item(current_item)
            current_item = None
            section = clean_markdown_item(heading.group(1))
            continue

        item = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.+)$", line)
        if item:
            add_item(current_item)
            current_item = item.group(1)
            if len(candidates) == MAX_CANDIDATES:
                rejected.append(
                    f"Stopped after {MAX_CANDIDATES} candidate principles."
                )
                break
            continue

        if current_item is not None and raw_line[:1].isspace() and line:
            current_item = f"{current_item} {line}"
            continue

        add_item(current_item)
        current_item = None

    add_item(current_item)

    return {
        "source_name": source_name,
        "candidates": candidates,
        "rejected": rejected
    }


def import_markdown(markdown, source_name, agent_id="human", approve=False):
    """Preview Markdown candidates or persist them after explicit approval."""
    preview = preview_markdown_import(markdown, source_name)
    preview["approved"] = bool(approve)
    preview["recorded"] = []

    if not approve:
        return preview

    principles = [candidate["task"] for candidate in preview["candidates"]]
    if principles:
        capture_principles(
            principles,
            owner=agent_id,
            source=preview["source_name"]
        )
        preview["recorded"] = preview["candidates"]

    return preview


def import_markdown_file(file_path, agent_id="human", approve=False):
    """Import a local Markdown file from the current project directory."""
    try:
        project_root = Path.cwd().resolve()
        path = Path(file_path).expanduser().resolve()
    except (OSError, TypeError, ValueError):
        return _file_error(file_path, "Markdown file path is invalid.", approve)

    try:
        path.relative_to(project_root)
    except ValueError:
        return _file_error(
            file_path,
            "Markdown file must be inside the current project directory.",
            approve
        )

    if path.suffix.lower() not in {".md", ".markdown"}:
        return _file_error(
            file_path,
            "File must have a .md or .markdown extension.",
            approve
        )

    if not path.is_file():
        return _file_error(file_path, "Markdown file was not found.", approve)

    if path.stat().st_size > MAX_MARKDOWN_BYTES:
        return _file_error(
            file_path,
            "Markdown file exceeds the 1 MB import limit.",
            approve
        )

    try:
        markdown = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return _file_error(
            file_path,
            "Markdown file could not be read as UTF-8.",
            approve
        )

    return import_markdown(
        markdown=markdown,
        source_name=path.name,
        agent_id=agent_id,
        approve=approve
    )


def _file_error(file_path, message, approve):
    return {
        "source_name": str(file_path),
        "candidates": [],
        "rejected": [message],
        "approved": bool(approve),
        "recorded": []
    }
