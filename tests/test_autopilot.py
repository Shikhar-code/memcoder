import os
import tempfile

from memory.autopilot import begin_event, control, failure_radar, finish_event, token_ledger


with tempfile.TemporaryDirectory() as directory:
    os.environ["MEMCODER_AUTOPILOT_PATH"] = os.path.join(directory, "autopilot.jsonl")

    first = begin_event(
        "task_started",
        "task-1",
        "tester",
        "Upgrade a dependency and publish a release",
        environment={"available_checks": ["python test_release.py"]},
    )
    assert first["should_intervene"] is True
    assert first["radar"]["risk"] == "high"
    assert first["verification_plan"]["checks"] == ["python test_release.py"]

    result = finish_event(first, intervention={
        "intervention": {"mode": "brief"},
        "receipt": {"id": "intervention-test"},
        "budget": {"estimated_tokens": 120},
    }, token_budget=450)
    assert result["attention"]["mode"] == "brief"
    assert result["ledger"]["net_token_dividend"] == 210

    repeated = finish_event(first, intervention={
        "intervention": {"mode": "brief"},
        "receipt": {"id": "intervention-test"},
        "budget": {"estimated_tokens": 120},
    }, token_budget=450)
    assert repeated["ledger"] == result["ledger"]
    assert len(token_ledger("tester", "task-1")["events"]) == 1

    duplicate = begin_event(
        "before_plan",
        "task-1",
        "tester",
        "Upgrade a dependency and publish a release",
        environment={"available_checks": ["python test_release.py"]},
    )
    assert duplicate["should_intervene"] is False
    assert duplicate["deduplicated"] is True

    assert control("pause", "tester")["state"] == "paused"
    paused = begin_event("context_changed", "task-1", "tester", "New context")
    assert paused["should_intervene"] is False
    assert control("resume", "tester")["state"] == "running"
    assert token_ledger("tester", "task-1")["totals"]["interventions"] == 1
    assert failure_radar("Explain a function")["risk"] == "normal"

os.environ.pop("MEMCODER_AUTOPILOT_PATH", None)
print("PASS: lifecycle autopilot")
