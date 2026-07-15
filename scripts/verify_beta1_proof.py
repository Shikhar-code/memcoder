"""Read-only evidence collector for the final Beta-1 MCP proof."""

import argparse
import os
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


def count_by_type(memories):
    return Counter(
        memory.get("type", "unknown")
        for memory in memories
    )


def validation_failures(
        counts,
        minimum_experiences,
        minimum_reflections):
    failures = []

    if counts["experience"] < minimum_experiences:
        failures.append(
            "Expected at least "
            f"{minimum_experiences} experience memory/memories."
        )

    if counts["reflection"] < minimum_reflections:
        failures.append(
            "Expected at least "
            f"{minimum_reflections} reflection memory/memories."
        )

    return failures


def main():
    parser = argparse.ArgumentParser(
        description="Verify a read-only Beta-1 memory proof."
    )

    parser.add_argument(
        "--owner",
        default="antigravity"
    )
    parser.add_argument(
        "--query",
        help="Optional related query to inspect retrieval."
    )
    parser.add_argument(
        "--db-path",
        help="Optional database path used for the controlled proof."
    )
    parser.add_argument(
        "--min-experiences",
        type=int,
        default=1
    )
    parser.add_argument(
        "--min-reflections",
        type=int,
        default=1
    )
    parser.add_argument(
        "--exclude-shared",
        action="store_true",
        help="Restrict the optional retrieval check to the proof owner."
    )

    args = parser.parse_args()

    if args.db_path:
        os.environ["MEMCODER_DB_PATH"] = args.db_path

    from memory.chroma_client import collection
    from memory.hierarchical_search import hierarchical_search

    data = collection.get(
        where={"owner": args.owner},
        include=["metadatas"]
    )

    memories = data["metadatas"]
    counts = count_by_type(memories)

    print("BETA-1 MEMORY PROOF")
    print(f"Owner: {args.owner}")
    print(f"Experiences: {counts['experience']}")
    print(f"Reflections: {counts['reflection']}")
    print(f"Principles: {counts['principle']}")
    print(f"Mistakes: {counts['mistake']}")

    for memory in memories[-5:]:
        print()
        print(f"[{memory.get('type', 'unknown')}]")
        print(memory.get("task", "Unknown"))

    failures = validation_failures(
        counts,
        args.min_experiences,
        args.min_reflections
    )

    if args.query:
        results = hierarchical_search(
            args.query,
            agent_id=args.owner,
            include_shared=not args.exclude_shared
        )

        print()
        print("RETRIEVAL CHECK")
        print(f"Confidence: {results['confidence']}")
        print(f"Strategy: {results['strategy']}")

        for memory_type in [
                "experiences",
                "reflections",
                "principles",
                "mistakes"]:
            for memory in results[memory_type]:
                print(
                    f"{memory_type}: "
                    f"{memory['task']} "
                    f"(distance={memory['score']:.3f})"
                )

    if failures:
        print()
        print("FAIL")

        for failure in failures:
            print(f"- {failure}")

        raise SystemExit(1)

    print()
    print("PASS: stored-memory evidence")


if __name__ == "__main__":
    main()
