"""Beta 3.0 local service boundaries remain deterministic and provider-free."""

import io
import json
import os
import tempfile
import gc
import threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from contextlib import redirect_stdout
from pathlib import Path

from memcoder import cli
from memory.capsule import build_capsule, verify_capsule
from memory.events import append_event, list_events
from memory.policy import evaluate_admission, redact_text, save_policy
from memory.replay import compare_cases
from memory.service import doctor, make_handler


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    os.environ["MEMCODER_POLICY_PATH"] = str(root / "policy.json")
    os.environ["MEMCODER_EVENT_JOURNAL_PATH"] = str(root / "events.jsonl")
    os.environ["MEMCODER_AUTOPILOT_PATH"] = str(root / "autopilot.jsonl")
    os.environ["MEMCODER_DREAM_PATH"] = str(root / "dreams.jsonl")
    os.environ["MEMCODER_REPLAY_PATH"] = str(root / "replays.jsonl")
    os.environ["MEMCODER_RECORD_DB_PATH"] = str(root / "records.sqlite3")
    os.environ["MEMCODER_DB_PATH"] = str(root / "chroma")

    save_policy({"admission": {"deny": ["**/.env"]}, "retrieval": {"allow_shared": False}})
    assert evaluate_admission(files=["src/app.py"], text=["safe"])["allowed"]
    blocked = evaluate_admission(files=["config/.env"], text=["safe"])
    assert not blocked["allowed"] and blocked["matched_rules"]
    assert redact_text("password:top-secret") == "password:[REDACTED]"

    first = append_event({"event_id": "event-1", "owner": "beta3", "event": "task_started"})
    duplicate = append_event({"event_id": "event-1", "owner": "beta3", "event": "task_started"})
    assert first["event_id"] == duplicate["event_id"]
    assert duplicate["deduplicated"] and len(list_events(owner="beta3")) == 1

    replay = compare_cases("validation task", [
        {"id": "baseline", "memory_ids": [], "tokens": 100, "rework": 2, "passed": False},
        {"id": "memcoder", "memory_ids": ["mem-1"], "tokens": 30, "rework": 0, "passed": True},
    ])
    assert replay["comparisons"][0]["token_delta"] == -70
    assert replay["comparisons"][0]["rework_delta"] == -2

    capsule = build_capsule(owner="beta3", project_id="demo")
    assert verify_capsule(capsule)["valid"]

    request = root / "policy-request.json"
    request.write_text(json.dumps({"action": "check", "files": [".env"]}), encoding="utf-8")
    output = io.StringIO()
    with redirect_stdout(output):
        assert cli.main(["policy", "--input", str(request)]) == 0
    assert json.loads(output.getvalue())["allowed"] is False

    replay_request = root / "replay-request.json"
    replay_request.write_text(json.dumps({
        "action": "compare",
        "task": "validation task",
        "cases": [
            {"id": "baseline", "tokens": 10, "rework": 1},
            {"id": "assisted", "tokens": 4, "rework": 0, "memory_ids": ["m-1"]},
        ],
    }), encoding="utf-8")
    output = io.StringIO()
    with redirect_stdout(output):
        assert cli.main(["replay", "--input", str(replay_request)]) == 0
    assert json.loads(output.getvalue())["comparisons"][0]["token_delta"] == -6

    capsule_request = root / "capsule-request.json"
    capsule_request.write_text(json.dumps({
        "action": "export",
        "output": str(root / "project.mcc"),
        "owner": "beta3",
        "project_id": "demo",
    }), encoding="utf-8")
    output = io.StringIO()
    with redirect_stdout(output):
        assert cli.main(["capsule", "--input", str(capsule_request)]) == 0
    assert json.loads(output.getvalue())["valid"] is True
    assert doctor()["provider_free"] is True

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    with urlopen(base + "/health") as response:
        assert json.loads(response.read())["ok"] is True
    with urlopen(base + "/") as response:
        assert b"MemCoder Studio" in response.read()
    with urlopen(base + "/v1/summary") as response:
        assert json.loads(response.read())["doctor"]["provider_free"] is True
    with urlopen(base + "/v1/records?limit=10") as response:
        records_response = json.loads(response.read())
        assert records_response["records"] == []
    demo_request = Request(
        base + "/v1/demo",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(demo_request) as response:
        demo = json.loads(response.read())
        assert demo["created"] is True
        assert demo["event_count"] >= 4
        assert demo["dreams"]
    with urlopen(demo_request) as response:
        assert json.loads(response.read())["created"] is False
    with urlopen(base + "/v1/events?owner=studio-demo") as response:
        assert len(json.loads(response.read())["events"]) >= 4
    with urlopen(base + "/v1/dreams?owner=all") as response:
        assert json.loads(response.read())["candidates"]
    dream_request = Request(
        base + "/v1/dream",
        data=json.dumps({"action": "run", "agent_id": "studio-demo", "max_candidates": 5}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(dream_request) as response:
        dream_response = json.loads(response.read())
        assert dream_response["owner"] == "studio-demo"
        assert "candidates" in dream_response
    with urlopen(base + "/v1/policy") as response:
        assert json.loads(response.read())["policy"]["retrieval"]["default_scope"] == "project"
    request = Request(
        base + "/v1/policy/check",
        data=json.dumps({"files": [".env"]}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        assert json.loads(response.read())["allowed"] is False
    request = Request(
        base + "/v1/capsule",
        data=json.dumps({"action": "export", "approved": True, "owner": "beta3"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        capsule_response = json.loads(response.read())
        assert capsule_response["valid"] is True
    request = Request(
        base + "/v1/storage/export",
        data=json.dumps({}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        assert json.loads(response.read())["allowed"] is False
    request = Request(
        base + "/v1/policy/retrieval",
        data=json.dumps({"owner": "beta3", "include_shared": True}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        assert json.loads(response.read())["allowed"] is False
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    gc.collect()

print("PASS: beta 3.0 local foundation")
