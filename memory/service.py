"""Small localhost API shared by adapters and the lightweight Memory Studio."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


STUDIO_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MemCoder Studio</title>
<style>
:root{font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;color:#e8edf5;background:#10151c;color-scheme:dark}
body{margin:0}main{max-width:1080px;margin:auto;padding:42px 24px 72px}header{display:flex;justify-content:space-between;gap:24px;align-items:start;border-bottom:1px solid #293342;padding-bottom:22px}h1{margin:0;font-size:34px;letter-spacing:-.04em}h2{font-size:14px;text-transform:uppercase;letter-spacing:.1em;color:#9ba8ba;margin:30px 0 10px}.muted{color:#9ba8ba}.health{white-space:nowrap;color:#72d4a1}.health:before{content:' ';display:inline-block;width:8px;height:8px;border-radius:50%;background:#72d4a1;margin-right:8px}button,input{font:inherit;color:inherit;background:#171e28;border:1px solid #354254;border-radius:6px;padding:8px 11px}button{cursor:pointer}button:hover{border-color:#78aefa}input{min-width:260px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.card{border:1px solid #293342;border-radius:9px;padding:15px;background:#141b24}.card strong{display:block;font-size:24px}.card span{color:#9ba8ba;font-size:13px}table{width:100%;border-collapse:collapse}th,td{text-align:left;border-top:1px solid #293342;padding:11px 8px 11px 0;vertical-align:top}th{font-size:11px;color:#9ba8ba;text-transform:uppercase;letter-spacing:.08em}a{color:#9ec5ff}pre{overflow:auto;background:#0b1016;border:1px solid #293342;border-radius:7px;padding:14px;font-size:12px}@media(max-width:620px){header{display:block}.health{display:block;margin-top:12px}input{min-width:0;width:100%;box-sizing:border-box}}
</style></head><body><main>
<header><div><h1>MemCoder Studio</h1><p class="muted">Local cognition you can inspect, replay, and control.</p></div><div class="health" id="health">checking service</div></header>
<section><h2>Overview</h2><div class="grid" id="cards"></div></section>
<section><h2>Recent memories</h2><input id="search" placeholder="Search task, summary, or solution"><div id="records" class="card" style="margin-top:12px">Loading…</div></section>
<section><h2>Raw diagnostics</h2><pre id="raw">Loading…</pre></section>
<script>
const $=s=>document.querySelector(s);let summary={};
async function get(path){const r=await fetch(path);if(!r.ok)throw Error(await r.text());return r.json()}
function draw(records){const q=($('#search').value||'').toLowerCase();const rows=records.filter(x=>!q||JSON.stringify(x).toLowerCase().includes(q)).slice(0,20);$('#records').innerHTML=rows.length?'<table><thead><tr><th>Type</th><th>Task</th><th>State</th></tr></thead><tbody>'+rows.map(x=>'<tr><td>'+esc(x.type||'memory')+'</td><td><strong>'+esc(x.task||x.summary||'Untitled')+'</strong><br><span class="muted">'+esc(x.summary||'')+'</span></td><td>'+esc(x.record_state||'trusted')+'</td></tr>').join('')+'</tbody></table>':'<span class="muted">No memories match this search.</span>'}
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function refresh(){try{summary=await get('/v1/summary');const s=summary.storage||{};$('#health').textContent=summary.doctor.healthy?'local service healthy':'attention required';$('#cards').innerHTML=[['Records',s.records||0,'durable memories'],['Events',summary.events?.events||0,'host receipts'],['Outcomes',summary.outcomes?.total||0,'closed-loop receipts'],['Dream candidates',s.dream_candidates||0,'sandboxed only'],['Provider','none','provider-free core']].map(x=>'<div class="card"><strong>'+esc(x[1])+'</strong><span>'+esc(x[0])+' · '+esc(x[2])+'</span></div>').join('');draw(await get('/v1/records?limit=100'));$('#raw').textContent=JSON.stringify(summary,null,2)}catch(e){$('#health').textContent='service unavailable';$('#raw').textContent=String(e)}}
$('#search').addEventListener('input',async()=>draw(await get('/v1/records?limit=100')));refresh();
</script></main></body></html>"""


def doctor():
    from memory.chroma_client import active_db_path
    from memory.events import journal_status
    from memory.policy import policy_status
    from memory.record_store import lexical_status, storage_path
    from memory.embedder import is_warm

    checks = []
    for name, path in (("record_store", storage_path()), ("semantic_index", active_db_path())):
        checks.append({"name": name, "path": str(path), "parent_exists": path.parent.exists()})
    checks.append({"name": "policy", **policy_status()})
    checks.append({"name": "event_journal", **journal_status()})
    return {
        "service": "memcoder",
        "version": "3.5",
        "provider_free": True,
        "offline_capable": True,
        "healthy": all(item.get("parent_exists", True) for item in checks),
        "checks": checks,
        "retrieval": {
            "lexical": lexical_status(),
            "semantic_warm": is_warm(),
            "cold_semantic_allowed": False,
            "fail_open": True,
        },
    }


def _json(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _html(handler, body):
    body = body.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _query(path):
    parsed = urlparse(path)
    return parsed.path, {key: values[-1] for key, values in parse_qs(parsed.query).items()}


def _limit(value, default=50, maximum=200):
    try:
        return max(1, min(maximum, int(value or default)))
    except (TypeError, ValueError):
        return default


def _records(query):
    from memory.record_store import list_records

    rows = list(reversed(list_records()))
    owner, state, kind, term = query.get("owner"), query.get("state"), query.get("type"), query.get("q", "").lower()
    if owner:
        rows = [row for row in rows if row.get("owner") == owner]
    if state:
        rows = [row for row in rows if row.get("record_state") == state]
    if kind:
        rows = [row for row in rows if row.get("type") == kind]
    if term:
        rows = [row for row in rows if term in json.dumps(row, ensure_ascii=False).lower()]
    return rows[:_limit(query.get("limit"))]


def summary():
    from memory.events import journal_status, list_events
    from memory.policy import policy_status
    from memory.storage_ops import storage_status
    from memory.utility import outcome_summary

    return {
        "doctor": doctor(),
        "events": journal_status(),
        "recent_events": list_events(limit=8),
        "hosts": host_summary(),
        "outcomes": outcome_summary(),
        "policy": policy_status(),
        "storage": storage_status(),
    }


def host_summary():
    """Return lightweight host-contract and local receipt activity."""
    from memory.contracts import host_manifest
    from memory.events import list_events

    events = list_events(limit=200)
    hosts = []
    for name in ("codex", "agy", "claude"):
        manifest = host_manifest(name)
        receipts = [item for item in events if item.get("host") == name]
        hosts.append({
            "host": name,
            "schema_version": manifest["schema_version"],
            "provider_free": manifest["provider_free"],
            "receipt_count": len(receipts),
            "last_event": receipts[-1].get("event") if receipts else None,
            "last_timestamp": receipts[-1].get("timestamp") if receipts else None,
        })
    return hosts


def _read_request(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length > 1_000_000:
        raise ValueError("request body is too large")
    value = json.loads(handler.rfile.read(length) or b"{}")
    if not isinstance(value, dict):
        raise ValueError("request body must be an object")
    return value


def _post(path, request):
    if path == "/v1/demo":
        from memory.events import list_events
        from api.cognition import autopilot_event_cognition
        from memory.dreaming import list_candidates

        owner = "studio-demo"
        environment = {"project_id": owner}
        existing = list_events(owner=owner, limit=1)
        if existing and list_candidates(owner):
            return {
                "created": False,
                "owner": owner,
                "message": "The guided Studio evidence already exists.",
                "dreams": list_candidates(owner),
            }

        examples = [
            {
                "task_id": "studio-demo-endpoint-input",
                "task": "Validate endpoint input safely",
                "summary": "Validated endpoint input before normalization.",
                "solution": "Checked required input, normalized it, and verified the expected result.",
            },
            {
                "task_id": "studio-demo-endpoint-config",
                "task": "Validate endpoint configuration safely",
                "summary": "Validated endpoint configuration before normalization.",
                "solution": "Checked required configuration, normalized it, and verified the expected result.",
            },
        ]
        receipts = []
        for example in examples:
            common = {
                "task_id": example["task_id"],
                "problem": example["task"],
                "agent_id": owner,
                "environment": environment,
            }
            for event in ("task_started", "before_plan", "verification_started"):
                receipts.append(autopilot_event_cognition(event=event, **common))
            receipts.append(autopilot_event_cognition(
                event="verification_finished",
                outcome={
                    "task": example["task"],
                    "files": [f"{example['task_id']}.py"],
                    "summary": example["summary"],
                    "solution": example["solution"],
                    "evidence": {"checks": [{
                        "name": "Studio guided assertion",
                        "kind": "assertion",
                        "status": "passed",
                        "assertion": "The normalized endpoint value is accepted.",
                        "actual": "The normalized endpoint value was accepted.",
                    }]},
                },
                **common,
            ))
            receipts.append(autopilot_event_cognition(event="task_completed", **common))

        from memory.record_store import list_records, save_record
        from memory.extractor import extract_memory
        from memory.records import initialize_record, searchable_document
        from memory.qa import evaluate_outcome_qa
        from memory.validity import attach_environment
        existing_tasks = {row.get("task") for row in list_records() if row.get("owner") == owner}
        for example in examples:
            if example["task"] in existing_tasks:
                continue
            evidence = {"checks": [{
                "name": "Studio Guided Assertion",
                "kind": "assertion",
                "status": "passed",
                "assertion": "The normalized endpoint value is accepted.",
                "actual": "The normalized endpoint value was accepted.",
            }]}
            qa = evaluate_outcome_qa(
                task=example["task"], files=[f"{example['task_id']}.py"],
                summary=example["summary"], solution=example["solution"], evidence=evidence,
            )
            if qa["verdict"] != "approved":
                continue
            memory = extract_memory(
                example["task"], [f"{example['task_id']}.py"], example["summary"],
                example["solution"], importance=5, memory_type="experience",
                verification=json.dumps({"qa_verdict": qa["verdict"], "evidence_summary": qa["evidence_summary"]}),
            )
            memory["owner"] = owner
            attach_environment(memory, environment)
            initialize_record(memory)
            save_record(memory, document=searchable_document(memory))

        # Keep the guided walkthrough inspectable even when an optional index
        # is unavailable; host lifecycle work remains fail-open by design.
        from memory.events import append_event
        recorded_events = {(item.get("task_id"), item.get("event")) for item in list_events(owner=owner)}
        for example in examples:
            for event in ("task_started", "before_plan", "verification_started", "verification_finished", "task_completed"):
                key = (example["task_id"], event)
                if key not in recorded_events:
                    append_event({
                        "kind": "lifecycle",
                        "owner": owner,
                        "task_id": example["task_id"],
                        "event": event,
                        "source": "studio_guided_demo",
                    })
        from memory.dreaming import list_candidates, run_dream
        run_dream(owner=owner, environment=environment)
        return {
            "created": True,
            "owner": owner,
            "message": "Created two QA-approved guided experiences and lifecycle evidence.",
            "event_count": len(list_events(owner=owner)),
            "dreams": list_candidates(owner),
        }
    if path == "/v1/policy/check":
        from memory.policy import evaluate_admission
        return evaluate_admission(**request)
    if path == "/v1/policy/retrieval":
        from memory.policy import evaluate_retrieval
        return evaluate_retrieval(**request)
    if path == "/v1/policy/export":
        from memory.policy import evaluate_export
        return evaluate_export(**request)
    if path == "/v1/policy/save":
        from memory.policy import save_policy
        return save_policy(request.get("policy"), request.get("path"))
    if path == "/v1/replay":
        from memory.replay import replay_action
        return replay_action(request.get("action", "compare"), request)
    if path == "/v1/capsule":
        from memory.capsule import capsule_action
        if request.get("action", "inspect") == "export" and not request.get("output"):
            from memory.record_store import storage_path
            request = {**request, "output": str(storage_path().parent / "exports" / "memcoder-capsule.mcc")}
        if request.get("action", "inspect") == "export":
            from memory.policy import evaluate_export
            decision = evaluate_export(
                owner=request.get("owner"),
                project_id=request.get("project_id"),
                include_shared=bool(request.get("include_shared", False)),
                approved=bool(request.get("approved", False)),
            )
            if not decision["allowed"]:
                return decision
        return capsule_action(request.get("action", "inspect"), request)
    if path == "/v1/autopilot":
        from api.cognition import autopilot_event_cognition
        return autopilot_event_cognition(**request)
    if path == "/v1/dream":
        from api.cognition import dream_cognition
        return dream_cognition(**request)
    if path == "/v1/storage/backup":
        from memory.storage_ops import create_backup
        return create_backup(request.get("output"))
    if path == "/v1/storage/export":
        from memory.storage_ops import export_snapshot
        from memory.policy import evaluate_export
        decision = evaluate_export(
            owner=request.get("owner"),
            project_id=request.get("project_id"),
            include_shared=bool(request.get("include_shared", False)),
            approved=bool(request.get("approved", False)),
        )
        if not decision["allowed"]:
            return decision
        return export_snapshot(request.get("output"))
    raise LookupError("not found")


def make_handler():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def _get(self):
            path, query = _query(self.path)
            if path in {"/", "/studio"}:
                _html(self, STUDIO_HTML)
                return
            if path == "/health":
                _json(self, 200, {"ok": True, "service": "memcoder", "version": "3.5"})
                return
            if path == "/v1/doctor":
                _json(self, 200, doctor())
                return
            if path == "/v1/summary":
                _json(self, 200, summary())
                return
            if path == "/v1/hosts":
                _json(self, 200, {"hosts": host_summary()})
                return
            if path == "/v1/outcomes":
                from memory.utility import outcome_summary
                _json(self, 200, outcome_summary(
                    owner=query.get("owner"),
                    memory_id=query.get("memory_id"),
                    limit=_limit(query.get("limit")),
                ))
                return
            if path == "/v1/records":
                records = _records(query)
                _json(self, 200, {"records": records, "count": len(records)})
                return
            if path.startswith("/v1/records/"):
                from memory.record_store import edges_for, get_record
                record_id = path.removeprefix("/v1/records/").strip("/")
                record = get_record(record_id)
                if record is None:
                    _json(self, 404, {"error": "record not found"})
                else:
                    _json(self, 200, {"record": record, "edges": edges_for(record_id, query.get("owner"))})
                return
            if path == "/v1/events":
                from memory.events import list_events
                _json(self, 200, {"events": list_events(owner=query.get("owner"), task_id=query.get("task_id"), limit=_limit(query.get("limit")))})
                return
            if path == "/v1/frontiers":
                from memory.failure_frontier import list_frontiers
                _json(self, 200, {"frontiers": list_frontiers(owner=query.get("owner"), status=query.get("status"))})
                return
            if path == "/v1/branches":
                from memory.cognitive_branch import list_branches
                branches = list_branches(owner=query.get("owner"), status=query.get("status"))
                if query.get("project_id"):
                    branches = [item for item in branches if item.get("project_id") == query["project_id"]]
                _json(self, 200, {"branches": branches})
                return
            if path == "/v1/dreams":
                from memory.dreaming import list_candidates, snapshot_candidates
                owner = query.get("owner", "human")
                if owner == "all":
                    candidates = snapshot_candidates()
                    if query.get("status"):
                        candidates = [item for item in candidates if item.get("status") == query["status"]]
                else:
                    candidates = list_candidates(owner, query.get("status"))
                _json(self, 200, {"candidates": candidates})
                return
            if path == "/v1/replays":
                from memory.replay import list_replays
                _json(self, 200, {"replays": list_replays()[-_limit(query.get("limit")): ]})
                return
            if path == "/v1/policy":
                from memory.policy import policy_status
                _json(self, 200, policy_status(query.get("path")))
                return
            _json(self, 404, {"error": "not found"})

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self):
            try:
                self._get()
            except Exception as error:
                _json(self, 500, {"available": False, "error": str(error)})

        def do_POST(self):
            try:
                path, _query_string = _query(self.path)
                result = _post(path, _read_request(self))
                _json(self, 200, result)
            except LookupError as error:
                _json(self, 404, {"error": str(error)})
            except (ValueError, KeyError, TypeError) as error:
                _json(self, 400, {"error": str(error)})
            except Exception as error:
                _json(self, 500, {"available": False, "error": str(error)})

    return Handler


def run_server(host="127.0.0.1", port=8765):
    server = ThreadingHTTPServer((host, int(port)), make_handler())
    print(json.dumps({"service": "memcoder", "host": host, "port": int(port), "provider_free": True}))
    try:
        server.serve_forever()
    finally:
        server.server_close()
