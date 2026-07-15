"""Read-only retrieval diagnostics for controlled Beta-1 evaluation."""

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from memory.relevance import memory_confidence


def format_candidate(memory):
    confidence = memory_confidence(memory)

    return (
        f"distance={memory['score']:.3f} "
        f"confidence={confidence:.2f} "
        f"task={memory.get('task', 'Unknown')}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Inspect raw and trusted MemCoder retrieval results."
    )

    parser.add_argument("query")
    parser.add_argument(
        "--owner",
        default="antigravity"
    )
    parser.add_argument(
        "--db-path",
        help="Optional database path used for the controlled proof."
    )

    args = parser.parse_args()

    if args.db_path:
        os.environ["MEMCODER_DB_PATH"] = args.db_path

    from memory.hierarchical_search import hierarchical_search
    from memory.relevance import MIN_MEMORY_CONFIDENCE
    from memory.search import search_memory

    raw_counts = {
        "experience": 5,
        "mistake": 5,
        "principle": 5,
        "reflection": 5
    }

    print("RAW RETRIEVAL DIAGNOSTIC")
    print(f"Query: {args.query}")
    print(f"Owner: {args.owner}")
    print(f"Minimum confidence: {MIN_MEMORY_CONFIDENCE:.2f}")

    for memory_type, count in raw_counts.items():
        candidates = search_memory(
            query=args.query,
            k=count,
            memory_type=memory_type,
            agent_id=args.owner
        )

        print()
        print(f"RAW {memory_type.upper()}S")

        if not candidates:
            print("none")

        for candidate in candidates:
            print(format_candidate(candidate))

    trusted = hierarchical_search(
        args.query,
        agent_id=args.owner
    )

    print()
    print("TRUSTED RETRIEVAL")
    print(f"Confidence: {trusted['confidence']:.2f}")
    print(f"Strategy: {trusted['strategy']}")

    for memory_type in [
            "experiences",
            "mistakes",
            "principles",
            "reflections"]:
        for candidate in trusted[memory_type]:
            print(
                f"{memory_type}: "
                f"{format_candidate(candidate)}"
            )


if __name__ == "__main__":
    main()
