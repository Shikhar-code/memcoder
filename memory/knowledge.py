"""Read-only, source-traceable Markdown knowledge for automation hosts.

Knowledge is intentionally separate from learned experiences, reflections,
mistakes, and principles. It represents approved project reference material,
not evidence learned from a verified outcome.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from memory import chroma_client
from memory.chroma_client import knowledge_collection
from memory.relevance import memory_confidence, query_terms


MAX_CHUNK_CHARS = 2_800
KNOWLEDGE_CONFIDENCE = 0.45
MANIFEST_VERSION = 1
CONFIG_VERSION = 1

UNSAFE_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "reveal the system prompt",
    "exfiltrate",
    "bypass safety",
    "disable safety",
)

MOJIBAKE_REPLACEMENTS = {
    "â€”": "-",
    "â€“": "-",
    "â†’": "->",
    "â†": "<-",
    "â€˜": "'",
    "â€™": "'",
    "â€œ": '"',
    "â€": '"',
    "â€¦": "...",
}

# Build these from code points so source-file encoding never changes the
# normalizer itself. The knowledge base contains these common UTF-8/Windows
# decoding artifacts.
MOJIBAKE_REPLACEMENTS = {
    "".join(map(chr, (0x00E2, 0x20AC, 0x201D))): "-",
    "".join(map(chr, (0x00E2, 0x20AC, 0x201C))): "-",
    "".join(map(chr, (0x00E2, 0x2020, 0x2019))): "->",
    "".join(map(chr, (0x00E2, 0x2020, 0x2018))): "<-",
    "".join(map(chr, (0x00E2, 0x20AC, 0x02DC))): "'",
    "".join(map(chr, (0x00E2, 0x20AC, 0x2122))): "'",
    "".join(map(chr, (0x00E2, 0x20AC, 0x0153))): '"',
    "".join(map(chr, (0x00E2, 0x20AC, 0x009D))): '"',
    "".join(map(chr, (0x00E2, 0x20AC, 0x00A6))): "...",
}


def normalize_knowledge_text(text):
    """Normalize common broken display sequences without altering source files."""
    normalized = str(text).replace("\r\n", "\n").replace("\r", "\n")
    for broken, replacement in MOJIBAKE_REPLACEMENTS.items():
        normalized = normalized.replace(broken, replacement)
    return normalized


def _safe_text(text):
    lowered = text.lower()
    return not any(pattern in lowered for pattern in UNSAFE_PATTERNS)


def _embed_one(text):
    """Load the embedding runtime only when a knowledge query needs it."""
    from memory.embedder import embed
    return embed(text)


def _embed_many(texts):
    """Load the embedding runtime only when changed source chunks need it."""
    from memory.embedder import embed_many
    return embed_many(texts)


def _category_from_path(path):
    return re.sub(r"^\d+_", "", path.stem).replace("_", " ")


def _split_sections(markdown):
    """Split a file by H1 document and H2 section, retaining hierarchy."""
    documents = []
    current_document = "Untitled document"
    current_section = "Overview"
    content = []

    def flush():
        body = "\n".join(content).strip()
        if body:
            documents.append((current_document, current_section, body))

    for line in markdown.splitlines():
        h1 = re.match(r"^#\s+(?!#)(.+?)\s*$", line)
        h2 = re.match(r"^##\s+(?!#)(.+?)\s*$", line)
        if h1:
            flush()
            current_document = h1.group(1).strip()
            current_section = "Overview"
            content = []
        elif h2:
            flush()
            current_section = h2.group(1).strip()
            content = []
        else:
            content.append(line)

    flush()
    return documents


def _split_large_body(body):
    """Chunk at paragraph boundaries, with a deterministic hard fallback."""
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", body) if item.strip()]
    chunks = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip()
        if current and len(candidate) > MAX_CHUNK_CHARS:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate

        while len(current) > MAX_CHUNK_CHARS:
            chunks.append(current[:MAX_CHUNK_CHARS])
            current = current[MAX_CHUNK_CHARS:].lstrip()

    if current:
        chunks.append(current)

    return chunks


def _source_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _chunk_id(relative_path, document, section, index, text):
    value = "\n".join((relative_path, document, section, str(index), text))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_knowledge_chunks(source_root, file_path):
    """Build provenance-rich chunks from one Markdown file without storing it."""
    source_root = Path(source_root).resolve()
    file_path = Path(file_path).resolve()
    relative_path = file_path.relative_to(source_root).as_posix()
    parts = Path(relative_path).parts
    subject = parts[0] if len(parts) > 1 else "general"
    category = _category_from_path(file_path)
    source_hash = _source_hash(file_path)
    markdown = normalize_knowledge_text(file_path.read_text(encoding="utf-8-sig"))
    chunks = []
    chunk_ordinal = 0

    for document, section, body in _split_sections(markdown):
        for index, body_chunk in enumerate(_split_large_body(body)):
            text = "\n".join((
                f"Subject: {subject}",
                f"Category: {category}",
                f"Document: {document}",
                f"Section: {section}",
                "",
                body_chunk,
            ))
            if not _safe_text(text):
                continue

            chunks.append({
                # Section-local indexes repeat across a concatenated source
                # file. A file-wide ordinal guarantees one Chroma ID per chunk.
                "id": _chunk_id(
                    relative_path,
                    document,
                    section,
                    chunk_ordinal,
                    text,
                ),
                "text": text,
                "metadata": {
                    "kind": "knowledge",
                    "source_root": str(source_root),
                    "source_path": relative_path,
                    "source_hash": source_hash,
                    "subject": subject,
                    "category": category,
                    "document": document,
                    "section": section,
                    "chunk_index": index,
                    "chunk_ordinal": chunk_ordinal,
                },
            })
            chunk_ordinal += 1

    return chunks


def _collection_records(where=None):
    result = knowledge_collection.get(
        where=where,
        include=["metadatas"],
    )
    return list(zip(result.get("ids", []), result.get("metadatas", [])))


def _delete_ids(ids):
    if ids:
        knowledge_collection.delete(ids=ids)


def _resolve_source_root(source_root):
    """Accept a downloaded archive folder that contains one Markdown root."""
    root = Path(source_root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Knowledge source directory was not found: {root}")

    direct_markdown = list(root.glob("*.md")) + list(root.glob("*.markdown"))
    directories = [path for path in root.iterdir() if path.is_dir()]
    if not direct_markdown and len(directories) == 1:
        return directories[0]
    return root


def _manifest_path():
    return Path(chroma_client.db_path) / "knowledge_manifest.json"


def default_knowledge_config_path():
    """Return the project-local automation configuration path."""
    return Path.cwd() / ".memcoder" / "knowledge.json"


def _resolve_config_path(config_path=None):
    path = Path(config_path) if config_path else default_knowledge_config_path()
    return path.expanduser().resolve()


def configure_knowledge(
        source_root,
        agent_id,
        config_path=None,
        include_shared=False):
    """Write a small, portable project contract for an automation host."""
    if not isinstance(agent_id, str) or not agent_id.strip():
        raise ValueError("Knowledge configuration requires a non-empty agent_id.")

    path = _resolve_config_path(config_path)
    payload = {
        "version": CONFIG_VERSION,
        "source_root": str(_resolve_source_root(source_root)),
        "agent_id": agent_id.strip(),
        "include_shared": bool(include_shared),
        "include_knowledge": True,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"config_path": str(path), **payload}


def load_knowledge_config(config_path=None):
    """Load and validate the project contract without syncing or embedding."""
    path = _resolve_config_path(config_path)
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read knowledge configuration: {path}") from error

    if not isinstance(config, dict) or config.get("version") != CONFIG_VERSION:
        raise ValueError("Knowledge configuration has an unsupported format.")
    if not isinstance(config.get("agent_id"), str) or not config["agent_id"].strip():
        raise ValueError("Knowledge configuration requires a non-empty agent_id.")
    if not isinstance(config.get("source_root"), str) or not config["source_root"].strip():
        raise ValueError("Knowledge configuration requires a source_root.")

    return {
        "config_path": str(path),
        "source_root": str(_resolve_source_root(config["source_root"])),
        "agent_id": config["agent_id"].strip(),
        "include_shared": bool(config.get("include_shared", False)),
        "include_knowledge": bool(config.get("include_knowledge", True)),
    }


def _load_manifest():
    path = _manifest_path()
    if not path.exists():
        return {"version": MANIFEST_VERSION, "sources": {}}

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": MANIFEST_VERSION, "sources": {}}

    if manifest.get("version") != MANIFEST_VERSION:
        return {"version": MANIFEST_VERSION, "sources": {}}
    manifest.setdefault("sources", {})
    return manifest


def _write_manifest(manifest):
    path = _manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _manifest_files_from_records(records):
    """Migrate one pre-manifest Chroma source without re-embedding it."""
    files = {}
    for identifier, metadata in records:
        source_path = metadata.get("source_path")
        if not source_path:
            continue
        entry = files.setdefault(source_path, {
            "source_hash": metadata.get("source_hash", ""),
            "chunk_ids": [],
            "subject": metadata.get("subject", "general"),
            "category": metadata.get("category", ""),
        })
        entry["chunk_ids"].append(identifier)
    return files


@contextmanager
def _knowledge_sync_lock():
    """Prevent two startup workers from mutating one knowledge index at once."""
    lock_path = Path(chroma_client.db_path) / ".knowledge_sync.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = None

    try:
        descriptor = os.open(
            lock_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
        )
    except FileExistsError as error:
        try:
            owner_pid = int(lock_path.read_text(encoding="utf-8").strip())
            os.kill(owner_pid, 0)
        except (OSError, ValueError):
            lock_path.unlink(missing_ok=True)
            descriptor = os.open(
                lock_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
        else:
            raise ValueError(
                "A MemCoder knowledge sync is already running for this index."
            ) from error

    try:
        os.write(descriptor, str(os.getpid()).encode("utf-8"))
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
            lock_path.unlink(missing_ok=True)


def sync_knowledge(source_root):
    """Synchronize an approved Markdown tree into the isolated knowledge index."""
    root = _resolve_source_root(source_root)

    with _knowledge_sync_lock():
        return _sync_knowledge_root(root)


def _sync_knowledge_root(root):
    """Synchronize after the caller has acquired the process-wide index lock."""

    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".markdown"}
    )
    root_key = str(root)
    manifest = _load_manifest()
    source_manifest = manifest["sources"].get(root_key)
    if source_manifest:
        previous_files = source_manifest.get("files", {})
        migration_records = []
    else:
        # Existing indexes created before manifests need one metadata scan. All
        # later syncs use the manifest and avoid this full-collection read.
        migration_records = _collection_records(where={"source_root": root_key})
        previous_files = _manifest_files_from_records(migration_records)

    report = {
        "source_root": root_key,
        "files_seen": len(files),
        "files_indexed": 0,
        "files_unchanged": 0,
        "files_rejected": [],
        "chunks_indexed": 0,
        "chunks_removed": 0,
    }
    seen_paths = set()
    next_files = {}

    for path in files:
        relative_path = path.relative_to(root).as_posix()
        seen_paths.add(relative_path)
        try:
            source_hash = _source_hash(path)
            previous = previous_files.get(relative_path)
            if previous and previous.get("source_hash") == source_hash:
                next_files[relative_path] = previous
                report["files_unchanged"] += 1
                continue

            chunks = build_knowledge_chunks(root, path)
        except (OSError, UnicodeDecodeError, ValueError) as error:
            if previous_files.get(relative_path):
                next_files[relative_path] = previous_files[relative_path]
            report["files_rejected"].append({
                "source_path": relative_path,
                "reason": str(error),
            })
            continue

        previous_ids = (previous or {}).get("chunk_ids", [])
        _delete_ids(previous_ids)
        report["chunks_removed"] += len(previous_ids)

        if chunks:
            knowledge_collection.upsert(
                ids=[chunk["id"] for chunk in chunks],
                documents=[chunk["text"] for chunk in chunks],
                embeddings=_embed_many([chunk["text"] for chunk in chunks]),
                metadatas=[chunk["metadata"] for chunk in chunks],
            )

        report["files_indexed"] += 1
        report["chunks_indexed"] += len(chunks)
        next_files[relative_path] = {
            "source_hash": source_hash,
            "chunk_ids": [chunk["id"] for chunk in chunks],
            "subject": chunks[0]["metadata"]["subject"] if chunks else "general",
            "category": chunks[0]["metadata"]["category"] if chunks else _category_from_path(path),
        }

    stale_ids = [
        identifier
        for source_path, entry in previous_files.items()
        if source_path not in seen_paths
        for identifier in entry.get("chunk_ids", [])
    ]
    _delete_ids(stale_ids)
    report["chunks_removed"] += len(stale_ids)
    manifest["sources"][root_key] = {
        "files": next_files,
        "chunks": sum(len(entry["chunk_ids"]) for entry in next_files.values()),
        "subjects": sorted({entry["subject"] for entry in next_files.values()}),
        "categories": sorted({entry["category"] for entry in next_files.values()}),
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_manifest(manifest)
    return report


def _knowledge_where(subject=None, category=None):
    filters = [{"kind": "knowledge"}]
    if subject:
        filters.append({"subject": subject})
    if category:
        filters.append({"category": category})
    return filters[0] if len(filters) == 1 else {"$and": filters}


def knowledge_status(source_root=None):
    """Report the current local knowledge index without running embeddings."""
    root_key = None
    if source_root is not None:
        root_key = str(_resolve_source_root(source_root))

    manifest = _load_manifest()
    sources = manifest["sources"]
    if root_key is None:
        selected = sources
    else:
        selected = {root_key: sources[root_key]} if root_key in sources else {}

    return {
        "source_root": root_key,
        "sources": len(selected),
        "chunks": sum(entry.get("chunks", 0) for entry in selected.values()),
        "files": sum(len(entry.get("files", {})) for entry in selected.values()),
        "subjects": sorted({
            subject
            for entry in selected.values()
            for subject in entry.get("subjects", [])
        }),
        "categories": sorted({
            category
            for entry in selected.values()
            for category in entry.get("categories", [])
        }),
        "synced_at": (
            selected[root_key].get("synced_at")
            if root_key in selected else None
        ),
    }


def _knowledge_text(record):
    return " ".join((
        record["subject"], record["category"], record["document"],
        record["section"], record["content"],
    ))


def search_knowledge(problem, subject=None, category=None, k=5):
    """Retrieve relevant, source-traceable reference knowledge."""
    if not isinstance(problem, str) or not problem.strip():
        return []

    # Do not initialize the embedding model for installations that have not
    # opted into a synced knowledge source yet.
    if knowledge_collection.count() == 0:
        return []

    results = knowledge_collection.query(
        query_embeddings=[_embed_one(problem)],
        n_results=k,
        where=_knowledge_where(subject=subject, category=category),
        include=["documents", "metadatas", "distances"],
    )
    documents = results.get("documents", [[]])[0]
    metadata_list = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    query_words = query_terms(problem)
    matches = []

    for document, metadata, distance in zip(documents, metadata_list, distances):
        record = {
            "content": document,
            "distance": float(distance),
            "subject": metadata.get("subject", "general"),
            "category": metadata.get("category", ""),
            "document": metadata.get("document", ""),
            "section": metadata.get("section", ""),
            "source_path": metadata.get("source_path", ""),
            "source_hash": metadata.get("source_hash", ""),
        }
        confidence = memory_confidence({"score": record["distance"]})
        overlap = len(query_words & query_terms(_knowledge_text(record)))
        if confidence >= KNOWLEDGE_CONFIDENCE or overlap > 0:
            record["confidence"] = round(confidence, 2)
            record["lexical_overlap"] = overlap
            record["relevance_score"] = round(
                confidence + min(overlap, 3) * 0.05,
                2,
            )
            matches.append(record)

    return sorted(matches, key=lambda record: record["relevance_score"], reverse=True)
