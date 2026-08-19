"""Beta 3.4 keeps automatic cognition bounded, cheap, and fail-open."""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from memory.hierarchical_search import hierarchical_search


class EmptyCollection:
    def __len__(self):
        return 0


with tempfile.TemporaryDirectory() as directory:
    with patch.dict(
            os.environ,
            {
                "MEMCODER_DB_PATH": os.path.join(directory, "chroma"),
                "MEMCODER_RECORD_DB_PATH": os.path.join(directory, "records.sqlite3"),
            },
            clear=False,
    ), patch("memory.hierarchical_search.collection", EmptyCollection()), patch(
            "memory.hierarchical_search.embed"
    ) as embed:
        result = hierarchical_search(
            "Fix the validation guard.",
            agent_id="beta34-empty",
        )
assert result["strategy"] == "normal_reasoning"
embed.assert_not_called()


with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_AUTOPILOT_PATH"] = os.path.join(directory, "autopilot.jsonl")
    os.environ["MEMCODER_UTILITY_PATH"] = os.path.join(directory, "utility.jsonl")
    os.environ["MEMCODER_DB_PATH"] = os.path.join(directory, "chroma")
    os.environ["MEMCODER_RECORD_DB_PATH"] = os.path.join(directory, "records.sqlite3")
    os.makedirs(os.environ["MEMCODER_DB_PATH"], exist_ok=True)
    Path(os.path.join(os.environ["MEMCODER_DB_PATH"], "chroma.sqlite3")).touch()
    with patch.dict(os.environ, {"MEMCODER_INTERVENTION_TIMEOUT_MS": "50"}):
        with patch("api.cognition.intervene_cognition", side_effect=lambda **_: time.sleep(0.2)):
            from api.cognition import autopilot_event_cognition

            started = time.perf_counter()
            timed_out = autopilot_event_cognition(
                event="task_started",
                task_id="beta34-timeout-1",
                problem="Investigate a slow validation integration.",
                agent_id="beta34-timeout",
            )
            elapsed = (time.perf_counter() - started) * 1000
            cooled_down = autopilot_event_cognition(
                event="task_started",
                task_id="beta34-timeout-2",
                problem="Investigate another slow validation integration.",
                agent_id="beta34-timeout",
            )

    assert timed_out["timeout_policy"]["timed_out"] is True
    assert timed_out["attention"]["timed_out"] is True
    assert elapsed < 180
    assert cooled_down["attention"]["gate"]["reason"] == "retrieval_circuit_open"
    assert cooled_down["cognition"] is None

    del os.environ["MEMCODER_AUTOPILOT_PATH"]
    del os.environ["MEMCODER_UTILITY_PATH"]
    del os.environ["MEMCODER_DB_PATH"]
    del os.environ["MEMCODER_RECORD_DB_PATH"]

from memory.benchmark import run_benchmark

benchmark = run_benchmark(iterations=2, timeout_ms=100)
assert benchmark["provider"] == "none"
assert benchmark["storage_touched"] is False
assert benchmark["latency_ms"]["p95"] >= 0
assert len(benchmark["samples"]) == 2

print("PASS: beta 3.4 reliability")
