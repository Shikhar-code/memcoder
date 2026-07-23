"""Deterministic cataloging and retrieval for approved visual assets.

Assets are source material for scene generation, not learned memories and not
Markdown knowledge chunks.  The catalog stores portable paths and descriptive
metadata; the automation host resolves those paths against its configured
asset-source directory.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ASSET_CATALOG_VERSION = 2
ASSET_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".mp4"}
SUBJECT_DIRECTORIES = {
    "assets_accounts": "accounts",
    "assets_chemistry": "chemistry",
    "assets_math": "math",
    "assets_physics": "physics",
    "bhavika_asset_bio": "biology",
    "economics assets": "economics",
}
STOP_WORDS = {
    "animation", "asset", "assets", "diagram", "icon", "scene", "svg",
    "png", "jpg", "image", "the", "and", "for", "with",
    # Exported SVGs often contain presentation-layer identifiers. They are not
    # educational concepts and must not become retrieval evidence.
    "cyan", "lavender", "glow", "gradient", "shadow", "fill", "stroke",
    "background", "foreground", "primary", "secondary", "accent", "layer",
}
VISUAL_TYPE_HINTS = {
    "labelled_diagram": ("diagram", "label", "formula"),
    "chart": ("chart", "curve", "graph", "scale"),
    "process_flow": ("flow", "cycle", "process", "pipeline"),
    "comparison": ("compare", "comparison", "versus", "vs"),
    "timeline": ("timeline", "history", "sequence"),
    "map": ("map", "geography", "globe"),
    "illustration": ("illustration", "object", "icon"),
}


def _tokens(value):
    # Asset exports frequently use camelCase names (for example,
    # ``DemandCurveAnimation``).  Treating that as one opaque token makes a
    # query for "demand curve" miss an otherwise relevant approved asset.
    normalized = str(value).replace("_", " ")
    normalized = re.sub(r"([a-z])([A-Z])", r"\1 \2", normalized)
    normalized = re.sub(r"([A-Za-z])([0-9])", r"\1 \2", normalized)
    normalized = re.sub(r"([0-9])([A-Za-z])", r"\1 \2", normalized)
    return [
        token.lower()
        for token in re.findall(r"[A-Za-z0-9]+", normalized)
        if len(token) > 1 and token.lower() not in STOP_WORDS
    ]


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _asset_id(relative_path):
    value = relative_path.as_posix().lower().encode("utf-8")
    return "asset_" + hashlib.sha256(value).hexdigest()[:20]


def _subject_for(relative_path):
    if not relative_path.parts:
        return "general"
    return SUBJECT_DIRECTORIES.get(relative_path.parts[0].lower(), "general")


def _load_economics_manifest(source_root):
    manifest_path = source_root / "Economics assets" / "manifest.json"
    if not manifest_path.is_file():
        return {}
    try:
        records = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    result = {}
    for record in records if isinstance(records, list) else []:
        if not isinstance(record, dict) or not isinstance(record.get("outFile"), str):
            continue
        result.setdefault(record["outFile"].lower(), []).append({
            "component": record.get("component"),
            "source_file": record.get("file"),
            "duplicate_of": record.get("duplicateOf", []),
        })
    return result


def _svg_dimensions(path):
    try:
        prefix = path.read_text(encoding="utf-8", errors="ignore")[:4096]
    except OSError:
        return {}
    match = re.search(r"<svg\b([^>]*)>", prefix, flags=re.IGNORECASE)
    if not match:
        return {}
    attributes = match.group(1)
    view_box = re.search(r'viewBox=["\']([^"\']+)["\']', attributes, re.IGNORECASE)
    if view_box:
        values = view_box.group(1).split()
        if len(values) == 4:
            try:
                return {"view_box": [float(value) for value in values]}
            except ValueError:
                pass
    return {}


def _svg_text_tags(path):
    """Extract descriptive SVG text without storing the SVG payload itself."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")[:131072]
    except OSError:
        return []
    values = re.findall(
        r"<(?:title|desc|text|tspan)\b[^>]*>(.*?)</(?:title|desc|text|tspan)>",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    values.extend(re.findall(
        r"(?:aria-label|data-label)=[\"']([^\"']+)[\"']", content,
        flags=re.IGNORECASE,
    ))
    cleaned = re.sub(r"<[^>]+>", " ", " ".join(values))
    return _tokens(cleaned)


def _infer_visual_types(tags):
    tag_set = set(tags)
    inferred = [
        visual_type for visual_type, hints in VISUAL_TYPE_HINTS.items()
        if tag_set.intersection(hints)
    ]
    return sorted(set(inferred or ["illustration"]))


def _load_metadata_overrides(metadata_path, source_root):
    """Load optional, path-keyed human curation without changing source files."""
    if metadata_path is None:
        return {}
    path = Path(metadata_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read asset metadata overrides: {error}") from error
    records = payload.get("assets", payload) if isinstance(payload, dict) else None
    if not isinstance(records, dict):
        raise ValueError("Asset metadata overrides must be a JSON object keyed by relative asset path.")
    valid = {}
    for relative_path, metadata in records.items():
        if not isinstance(relative_path, str) or not isinstance(metadata, dict):
            continue
        normalized = relative_path.replace("\\", "/").lstrip("/")
        if ".." in Path(normalized).parts or not (source_root / normalized).is_file():
            continue
        valid[normalized.lower()] = metadata
    return valid


def _metadata_strings(metadata, field):
    value = metadata.get(field, [])
    if isinstance(value, str):
        value = [value]
    return _tokens(" ".join(item for item in value if isinstance(item, str))) if isinstance(value, list) else []


def _metadata_values(metadata, field):
    """Keep enumerated metadata stable for exact comparisons downstream."""
    value = metadata.get(field, [])
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [
        re.sub(r"[\s-]+", "_", item.strip().lower())
        for item in value
        if isinstance(item, str) and item.strip()
    ]


def build_asset_catalog(source_root, subject=None, metadata_path=None):
    """Return a deterministic asset manifest for one approved source folder."""
    source_root = Path(source_root).resolve()
    if not source_root.is_dir():
        raise ValueError(f"Asset source directory does not exist: {source_root}")
    requested_subject = subject.strip().lower() if isinstance(subject, str) and subject.strip() else None

    economics_manifest = _load_economics_manifest(source_root)
    metadata_overrides = _load_metadata_overrides(metadata_path, source_root)
    assets = []
    for path in sorted(source_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in ASSET_EXTENSIONS:
            continue
        relative_path = path.relative_to(source_root)
        subject = _subject_for(relative_path)
        if requested_subject and subject != requested_subject:
            continue
        tags = _tokens(relative_path.parent) + _tokens(path.stem)
        if path.suffix.lower() == ".svg":
            tags.extend(_svg_text_tags(path))
        manifest_entries = economics_manifest.get(path.name.lower(), [])
        for entry in manifest_entries:
            tags.extend(_tokens(entry.get("component", "")))
        metadata = metadata_overrides.get(relative_path.as_posix().lower(), {})
        tags.extend(_metadata_strings(metadata, "tags"))
        concepts = sorted(set(_metadata_strings(metadata, "concepts")))
        concept_phrases = sorted(set(_metadata_values(metadata, "concepts")))
        visual_types = _metadata_values(metadata, "visual_types")
        tags = sorted(set(tags))
        record = {
            "id": _asset_id(relative_path),
            "path": relative_path.as_posix(),
            "subject": subject,
            "kind": path.suffix.lower().lstrip("."),
            "tags": tags,
            "concepts": concepts,
            "concept_phrases": concept_phrases,
            "visual_types": sorted(set(visual_types or _infer_visual_types(tags))),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
            "review_status": metadata.get("review_status", "unreviewed"),
        }
        if path.suffix.lower() == ".svg":
            record.update(_svg_dimensions(path))
        if isinstance(metadata.get("grade_levels"), list):
            record["grade_levels"] = sorted(set(_metadata_values(metadata, "grade_levels")))
        if manifest_entries:
            record["source_components"] = manifest_entries
            record["metadata_provenance"] = "economics_manifest"
        assets.append(record)

    records_by_hash = defaultdict(list)
    for record in assets:
        records_by_hash[record["sha256"]].append(record)
    for records in records_by_hash.values():
        canonical = next(
            (record for record in records if record.get("source_components")),
            records[0],
        )
        for record in records:
            if record is not canonical:
                record["duplicate_of"] = canonical["id"]

    return {
        "schema_version": ASSET_CATALOG_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "asset_count": len(assets),
        "subjects": sorted({record["subject"] for record in assets}),
        "metadata_overrides": str(Path(metadata_path).resolve()) if metadata_path else None,
        "assets": assets,
    }


def write_asset_catalog(source_root, output_path, subject=None, metadata_path=None):
    catalog = build_asset_catalog(source_root, subject=subject, metadata_path=metadata_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return {
        "catalog": str(output_path.resolve()),
        "asset_count": catalog["asset_count"],
        "subjects": catalog["subjects"],
        "schema_version": catalog["schema_version"],
        "subject": subject.strip().lower() if isinstance(subject, str) and subject.strip() else None,
        "metadata": str(Path(metadata_path).resolve()) if metadata_path else None,
    }


def load_asset_catalog(catalog_path):
    try:
        catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read asset catalog: {error}") from error
    if not isinstance(catalog, dict) or catalog.get("schema_version") != ASSET_CATALOG_VERSION:
        raise ValueError("Asset catalog has an unsupported schema version.")
    if not isinstance(catalog.get("assets"), list):
        raise ValueError("Asset catalog must contain an assets list.")
    return catalog


def search_assets(catalog_path, query, subject=None, limit=8):
    """Return deterministic metadata matches; never load or embed the binaries."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Asset search query must be a non-empty string.")
    if subject is not None and (not isinstance(subject, str) or not subject.strip()):
        raise ValueError("Asset search subject must be a non-empty string when provided.")
    if not isinstance(limit, int) or limit < 1 or limit > 50:
        raise ValueError("Asset search limit must be between 1 and 50.")

    query_tokens = set(_tokens(query))
    requested_subject = subject.strip().lower() if subject else None
    matches = []
    for record in load_asset_catalog(catalog_path)["assets"]:
        if requested_subject and record.get("subject") != requested_subject:
            continue
        tags = set(record.get("tags", [])) | set(record.get("concepts", []))
        overlap = len(query_tokens & tags)
        if overlap == 0:
            continue
        score = overlap * 10 + (3 if requested_subject else 0)
        matches.append({
            "id": record["id"],
            "path": record["path"],
            "subject": record["subject"],
            "kind": record["kind"],
            "tags": record["tags"],
            "concepts": record.get("concepts", []),
            "visual_types": record.get("visual_types", []),
            "review_status": record["review_status"],
            "score": score,
            **({"duplicate_of": record["duplicate_of"]} if record.get("duplicate_of") else {}),
        })

    matches.sort(
        key=lambda item: (-item["score"], bool(item.get("duplicate_of")), item["path"])
    )
    return {
        "query": query.strip(),
        "subject": requested_subject,
        "matches": matches[:limit],
    }
