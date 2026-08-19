"""Small provider-free lifecycle benchmark for Beta 3.5 release diagnostics."""

import math
import os
import tempfile
import time


_ISOLATED_VARS = (
    "MEMCODER_AUTOPILOT_PATH",
    "MEMCODER_EVENT_JOURNAL_PATH",
    "MEMCODER_UTILITY_PATH",
    "MEMCODER_DB_PATH",
    "MEMCODER_RECORD_DB_PATH",
    "MEMCODER_FAILURE_FRONTIER_PATH",
    "MEMCODER_POLICY_PATH",
    "MEMCODER_INTERVENTION_TIMEOUT_MS",
)


def _percentile(values, fraction):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * fraction) - 1))
    return round(ordered[index], 2)


def run_benchmark(iterations=5, timeout_ms=None):
    """Measure the automatic boundary without touching the user's memory."""
    iterations = max(1, min(100, int(iterations)))
    previous = {name: os.environ.get(name) for name in _ISOLATED_VARS}
    with tempfile.TemporaryDirectory(prefix="memcoder-benchmark-") as directory:
        os.environ["MEMCODER_AUTOPILOT_PATH"] = os.path.join(directory, "autopilot.jsonl")
        os.environ["MEMCODER_EVENT_JOURNAL_PATH"] = os.path.join(directory, "events.jsonl")
        os.environ["MEMCODER_UTILITY_PATH"] = os.path.join(directory, "utility.jsonl")
        os.environ["MEMCODER_DB_PATH"] = os.path.join(directory, "chroma")
        os.environ["MEMCODER_RECORD_DB_PATH"] = os.path.join(directory, "records.sqlite3")
        os.environ["MEMCODER_FAILURE_FRONTIER_PATH"] = os.path.join(directory, "frontiers.jsonl")
        os.environ["MEMCODER_POLICY_PATH"] = os.path.join(directory, "policy.json")
        if timeout_ms is not None:
            os.environ["MEMCODER_INTERVENTION_TIMEOUT_MS"] = str(timeout_ms)
        try:
            from api.cognition import autopilot_event_cognition

            samples = []
            results = []
            for index in range(iterations):
                started = time.perf_counter()
                result = autopilot_event_cognition(
                    event="task_started",
                    task_id=f"benchmark-{index}",
                    problem="Benchmark the automatic MemCoder lifecycle boundary.",
                    agent_id="benchmark",
                    environment={"project_id": "benchmark"},
                    token_budget=160,
                )
                elapsed = (time.perf_counter() - started) * 1000
                samples.append(round(elapsed, 2))
                results.append(result)
            timed_out = sum(
                bool(result.get("timeout_policy", {}).get("timed_out"))
                for result in results
            )
            from memory.record_store import save_record
            save_record({
                "task": "Fix webhook endpoint validation",
                "files": ["webhook.py"],
                "summary": "Endpoint input reached normalization before validation.",
                "solution": "Validate endpoint_name before calling string operations.",
                "type": "experience",
                "owner": "benchmark",
                "verification": '{"qa_verdict":"approved"}',
            })
            lexical_samples = []
            lexical_results = []
            for index in range(iterations):
                started = time.perf_counter()
                lexical_results.append(autopilot_event_cognition(
                    event="task_started",
                    task_id=f"benchmark-lexical-{index}",
                    problem="Fix webhook endpoint_name validation safely.",
                    agent_id="benchmark",
                    include_shared=False,
                    environment={"project_id": "benchmark"},
                    token_budget=250,
                ))
                lexical_samples.append(round((time.perf_counter() - started) * 1000, 2))
            return {
                "iterations": iterations,
                "latency_ms": {
                    "median": _percentile(samples, 0.50),
                    "p95": _percentile(samples, 0.95),
                    "max": round(max(samples), 2) if samples else 0.0,
                },
                "timed_out": timed_out,
                "timeout_rate": round(timed_out / iterations, 3),
                "modes": sorted({
                    result.get("attention", {}).get("mode", "none")
                    for result in results
                }),
                "provider": "none",
                "storage_touched": False,
                "samples": samples,
                "lexical_fallback": {
                    "latency_ms": {
                        "median": _percentile(lexical_samples, 0.50),
                        "p95": _percentile(lexical_samples, 0.95),
                        "max": round(max(lexical_samples), 2) if lexical_samples else 0.0,
                    },
                    "interventions": sum(
                        result.get("attention", {}).get("mode") != "none"
                        for result in lexical_results
                    ),
                    "within_150ms": _percentile(lexical_samples, 0.95) <= 150,
                },
            }
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
