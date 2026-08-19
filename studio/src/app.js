const API = "http://127.0.0.1:8765";
const view = document.querySelector("#view");
const title = document.querySelector("#view-title");
const status = document.querySelector("#service-status");
const statusDot = document.querySelector("#status-dot");
const notice = document.querySelector("#notice");
let currentView = "home";
let pendingReplay = null;
let dreamOwner = "studio-demo";

const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[char]));

function titleCase(value) {
  const words = String(value ?? "").replace(/[_-]+/g, " ").trim().split(/\s+/);
  return words.map((word) => {
    const upper = word.toUpperCase();
    if (["API", "JSON", "QA", "UI", "URL"].includes(upper)) return upper;
    return word ? word[0].toUpperCase() + word.slice(1).toLowerCase() : word;
  }).join(" ");
}

const STATE_LABELS = {
  trusted: "Verified",
  candidate: "Awaiting Evidence",
  withheld: "Not Admitted",
  sandboxed: "Evidence Passed",
  promoted: "Added To Memory",
  rejected: "Rejected",
  rolled_back: "Rolled Back",
};

function stateLabel(value) { return STATE_LABELS[value] || titleCase(value || "Unknown"); }
function stateClass(value) { return `state-${String(value || "unknown").replace(/[^a-z0-9]+/gi, "-").toLowerCase()}`; }
function stateTag(value) { return `<span class="state ${stateClass(value)}"><span class="state-dot"></span>${esc(stateLabel(value))}</span>`; }

function dash(value) { return value == null || value === "" ? "-" : value; }

async function api(path, options) {
  const response = await fetch(API + path, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

function showError(error) {
  notice.textContent = error.message || String(error);
  notice.className = "notice";
}

function showNotice(message) {
  notice.textContent = message;
  notice.className = "notice success";
}

function clearError() { notice.className = "notice hidden"; }

function metric(value, label) {
  return `<div class="metric"><span class="metric-value">${esc(value)}</span><span class="metric-label">${esc(label)}</span></div>`;
}

function sectionHeading(heading, description = "", action = "") {
  return `<div class="section-head"><div><h2>${esc(heading)}</h2>${description ? `<p class="hint">${esc(description)}</p>` : ""}</div>${action}</div>`;
}

function setBusy(message) { status.textContent = message; }

async function loadGuidedDemo(after = null) {
  try {
    clearError();
    setBusy("Loading Guided Evidence...");
    const result = await api("/v1/demo", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    showNotice(result.message || "Guided evidence is ready.");
    if (after) await after();
  } catch (error) {
    showError(error);
  } finally {
    setBusy("Local Service Healthy");
  }
}

async function renderHome() {
  const data = await api("/v1/summary");
  const storage = data.storage || {};
  const doctor = data.doctor || {};
  const recent = (data.recent_events || []).slice().reverse();
  view.innerHTML = `<div class="section"><div class="grid">
    ${metric(storage.records || 0, "Durable Memories")}
    ${metric(data.events?.events || 0, "Lifecycle Events")}
    ${metric(data.outcomes?.total || 0, "Outcome Receipts")}
    ${metric(storage.dream_candidates || 0, "Dream Candidates")}
    ${metric(doctor.provider_free ? "None" : "Configured", "Provider Required")}
  </div></div>
  <div class="section"><div class="callout"><strong>Local Control Is Active.</strong> MemCoder admits verified outcomes, keeps candidates separate, and exposes every automatic boundary for inspection.</div></div>
  <div class="section">${sectionHeading("Supported Hosts", "One provider-free lifecycle contract across local adapters.")}<div class="host-grid">${(data.hosts || []).map((item) => `<div class="panel host-card"><div class="host-card-head"><strong>${esc(titleCase(item.host))}</strong><span class="host-version">Contract ${esc(item.schema_version)}</span></div><p class="hint">${item.receipt_count ? `${esc(item.receipt_count)} lifecycle receipt${item.receipt_count === 1 ? "" : "s"}` : "No receipts yet"}</p><p class="muted">${item.last_event ? `Last: ${esc(titleCase(item.last_event))}` : "Ready for host setup and certification"}</p></div>`).join("")}</div></div>
  <div class="section">${sectionHeading("Recent Activity", "The latest host receipts, not raw conversations.", `<button class="button quiet" id="home-demo">Load Guided Demo</button>`)}
    <div class="panel">${recent.length ? `<div class="table-wrap"><table><thead><tr><th>Event</th><th>Task</th><th>Time</th></tr></thead><tbody>${recent.map((item) => eventRow(item, false)).join("")}</tbody></table></div>` : empty("No lifecycle events yet. Load the guided demo to see verified evidence.")}</div>
  </div>
  <div class="section">${sectionHeading("Health", "Filesystem and local policy checks.")}<div class="panel panel-pad"><pre>${esc(JSON.stringify(doctor.checks || [], null, 2))}</pre></div></div>`;
  document.querySelector("#home-demo").addEventListener("click", () => loadGuidedDemo(renderHome));
}

function eventRow(item, includeOwner = true) {
  const owner = includeOwner ? `<td>${esc(dash(item.owner))}</td>` : "";
  return `<tr><td><span class="event-name">${esc(titleCase(item.event || "Event"))}</span></td><td>${esc(dash(item.task_id || item.owner))}</td>${owner}<td class="muted">${esc(dash(item.timestamp))}</td></tr>`;
}

function empty(text) { return `<div class="empty">${esc(text)}</div>`; }

async function renderMemories() {
  view.innerHTML = `<div class="section">${sectionHeading("Memories", "Search the durable source of truth; retrieval indexes remain replaceable.", `<button class="button quiet" id="refresh">Refresh</button>`)}
    <div class="panel panel-pad"><div class="toolbar"><input class="search" id="memory-search" placeholder="Search task, summary, or solution..."><select id="memory-state"><option value="">All States</option><option value="trusted">Verified</option><option value="candidate">Awaiting Evidence</option><option value="withheld">Not Admitted</option></select></div></div>
    <div class="panel" style="margin-top:12px" id="memory-list">Loading...</div></div>`;
  const load = async () => {
    const params = new URLSearchParams({ limit: "100" });
    const term = document.querySelector("#memory-search").value.trim();
    const state = document.querySelector("#memory-state").value;
    if (term) params.set("q", term); if (state) params.set("state", state);
    const data = await api(`/v1/records?${params}`);
    const list = document.querySelector("#memory-list");
    list.innerHTML = data.records?.length ? `<div class="table-wrap"><table><thead><tr><th>Kind</th><th>Task</th><th>State</th><th>Updated</th></tr></thead><tbody>${data.records.map(recordRow).join("")}</tbody></table></div>` : empty("No memories match this view.");
    list.querySelectorAll("tr[data-id]").forEach((row) => row.addEventListener("click", () => openRecord(row.dataset.id)));
  };
  document.querySelector("#memory-search").addEventListener("input", load);
  document.querySelector("#memory-state").addEventListener("change", load);
  document.querySelector("#refresh").addEventListener("click", load);
  await load();
}

function recordRow(record) {
  const state = record.record_state || "trusted";
  return `<tr class="clickable" data-id="${esc(record.record_id)}"><td>${esc(titleCase(record.type || "Memory"))}</td><td><strong>${esc(record.task || record.summary || "Untitled")}</strong><br><span class="muted">${esc(record.summary || "")}</span></td><td>${stateTag(state)}</td><td class="muted">${esc(dash(record.updated_at || record.created_at))}</td></tr>`;
}

async function openRecord(id) {
  try {
    const data = await api(`/v1/records/${encodeURIComponent(id)}`);
    view.insertAdjacentHTML("beforeend", `<div class="section" id="record-detail">${sectionHeading("Memory Detail", "Evidence and provenance for the selected record.", `<button class="button quiet" id="close-detail">Close</button>`)}<div class="detail"><div class="panel panel-pad"><h3>${esc(data.record.task || "Untitled")}</h3><p class="hint" style="margin-top:8px">${esc(data.record.summary || "")}</p><h3 style="margin-top:22px">Solution</h3><p style="margin-top:8px">${esc(data.record.solution || "")}</p></div><div class="panel panel-pad"><h3>Record Metadata</h3><pre style="margin-top:10px">${esc(JSON.stringify({ record_id: data.record.record_id, type: data.record.type, state: data.record.record_state, owner: data.record.owner, revision: data.record.revision }, null, 2))}</pre><h3 style="margin-top:18px">Provenance</h3><pre style="margin-top:10px">${esc(JSON.stringify(data.edges || [], null, 2))}</pre></div></div></div>`);
    document.querySelector("#close-detail").addEventListener("click", () => document.querySelector("#record-detail")?.remove());
    document.querySelector("#record-detail").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { showError(error); }
}

async function renderEvidence() {
  const [data, frontiers, branches, outcomes] = await Promise.all([api("/v1/events?limit=100"), api("/v1/frontiers"), api("/v1/branches"), api("/v1/outcomes?limit=30")]);
  view.innerHTML = `<div class="section">${sectionHeading("Evidence Timeline", "Host events are append-only and idempotent; they are not treated as memories.", `<button class="button" id="evidence-demo">Load Guided Demo</button>`)}<div class="panel">${data.events?.length ? `<div class="table-wrap"><table><thead><tr><th>Event</th><th>Task</th><th>Owner</th><th>Timestamp</th></tr></thead><tbody>${data.events.slice().reverse().map((item) => eventRow(item, true)).join("")}</tbody></table></div>` : empty("No lifecycle events yet. Load the guided demo to create inspectable evidence.")}</div></div>
  <div class="section">${sectionHeading("Intervention Outcomes", "Predictions close only when the host reports use and verification.")}<div class="panel">${outcomes.recent?.length ? `<div class="table-wrap"><table><thead><tr><th>Prediction</th><th>Guidance Used</th><th>Action Changed</th><th>Verified</th><th>Time</th></tr></thead><tbody>${outcomes.recent.map((item) => `<tr><td>${esc(titleCase(item.prediction_status || "Inconclusive"))}</td><td>${esc(item.guidance_used == null ? "Not Reported" : item.guidance_used ? "Yes" : "No")}</td><td>${esc(item.changed_action == null ? "Not Reported" : item.changed_action ? "Yes" : "No")}</td><td>${esc(item.verification_passed == null ? "Not Reported" : item.verification_passed ? "Passed" : "Did Not Pass")}</td><td class="muted">${esc(dash(item.timestamp))}</td></tr>`).join("")}</tbody></table></div>` : empty("No closed-loop outcomes yet.")}</div></div>
  <div class="section">${sectionHeading("Failure Frontiers", "Known risks stay warnings until a later host verification proves them useful.")}<div class="panel">${frontiers.frontiers?.length ? `<div class="table-wrap"><table><thead><tr><th>Trigger</th><th>Warning</th><th>State</th></tr></thead><tbody>${frontiers.frontiers.map((item) => `<tr><td>${esc(item.trigger)}</td><td>${esc(item.warning)}<br><span class="muted">Check: ${esc(item.verification)}</span></td><td>${stateTag(item.status)}</td></tr>`).join("")}</tbody></table></div>` : empty("No failure frontiers recorded.")}</div></div>
  <div class="section">${sectionHeading("Cognitive Branches", "Alternative decisions remain isolated until their proof obligations pass.")}<div class="panel">${branches.branches?.length ? `<div class="table-wrap"><table><thead><tr><th>Name</th><th>Project</th><th>State</th></tr></thead><tbody>${branches.branches.map((item) => `<tr><td>${esc(item.name)}</td><td>${esc(dash(item.project_id))}</td><td>${stateTag(item.status)}</td></tr>`).join("")}</tbody></table></div>` : empty("No cognitive branches recorded.")}</div></div>`;
  document.querySelector("#evidence-demo").addEventListener("click", () => loadGuidedDemo(renderEvidence));
}

function readReplayCase(form, prefix, fallbackId) {
  const passed = form.get(`${prefix}-passed`);
  return {
    id: String(form.get(`${prefix}-id`) || fallbackId).trim(),
    label: String(form.get(`${prefix}-label`) || fallbackId).trim(),
    strategy: String(form.get(`${prefix}-strategy`) || "unknown").trim(),
    tokens: Number(form.get(`${prefix}-tokens`) || 0),
    rework: Number(form.get(`${prefix}-rework`) || 0),
    passed: passed === "true" ? true : passed === "false" ? false : null,
    memory_ids: String(form.get(`${prefix}-memories`) || "").split(",").map((item) => item.trim()).filter(Boolean),
  };
}

function deltaText(value, unit) {
  if (value == null) return "Not Reported";
  const number = Number(value);
  if (!number) return `No Change in ${titleCase(unit)}`;
  return `${number < 0 ? "↓" : "↑"} ${Math.abs(number)} ${titleCase(unit)}`;
}

function replayResult(replay) {
  const comparison = replay.comparisons?.[0] || {};
  const assisted = replay.cases?.[1] || {};
  const passed = assisted.passed === true ? "Passed" : assisted.passed === false ? "Did Not Pass" : "Not Reported";
  return `<div class="comparison"><div><span class="comparison-label">Assisted Run</span><strong>${esc(passed)}</strong></div><div><span class="comparison-label">Token Change</span><strong>${esc(deltaText(comparison.token_delta, "Tokens"))}</strong></div><div><span class="comparison-label">Rework Change</span><strong>${esc(deltaText(comparison.rework_delta, "Rework Attempts"))}</strong></div><div><span class="comparison-label">Memories Added</span><strong>${esc(comparison.memory_added?.length || 0)}</strong></div></div>`;
}

async function renderReplay() {
  const data = await api("/v1/replays?limit=30");
  pendingReplay = null;
  view.innerHTML = `<div class="section">${sectionHeading("Replay Lab", "Compare two captured runs. Replay Lab records evidence; it does not rerun the task.")}
  <div class="panel panel-pad"><form id="replay-form"><div class="form-grid"><label class="wide">Task<input name="task" required placeholder="Validate a webhook endpoint safely"></label></div><div class="case-grid">
    <fieldset class="case-card"><legend>Baseline Run</legend><label>Label<input name="baseline-label" value="Baseline Run"></label><input type="hidden" name="baseline-id" value="baseline"><label>Strategy<input name="baseline-strategy" value="No Memory"></label><label>Result<select name="baseline-passed"><option value="false">Did Not Pass</option><option value="true">Passed</option><option value="unknown">Not Reported</option></select></label><label>Tokens Used<input type="number" name="baseline-tokens" min="0" value="100"></label><label>Rework Attempts<input type="number" name="baseline-rework" min="0" value="2"></label><label>Memory IDs <span class="muted">(optional)</span><input name="baseline-memories" placeholder="Leave blank if none"></label></fieldset>
    <fieldset class="case-card"><legend>MemCoder-Assisted Run</legend><label>Label<input name="assisted-label" value="MemCoder-Assisted Run"></label><input type="hidden" name="assisted-id" value="assisted"><label>Strategy<input name="assisted-strategy" value="MemCoder"></label><label>Result<select name="assisted-passed"><option value="true">Passed</option><option value="false">Did Not Pass</option><option value="unknown">Not Reported</option></select></label><label>Tokens Used<input type="number" name="assisted-tokens" min="0" value="70"></label><label>Rework Attempts<input type="number" name="assisted-rework" min="0" value="0"></label><label>Memory IDs <span class="muted">(optional)</span><input name="assisted-memories" placeholder="memory-id-1, memory-id-2"></label></fieldset>
  </div><div class="form-actions"><button class="button" type="button" id="preview-replay">Preview Comparison</button><button class="button quiet" type="button" id="save-replay" disabled>Save Replay Evidence</button></div></form><div id="replay-result" class="result-slot"></div></div>
  <div class="section">${sectionHeading("Saved Comparisons")}<div class="panel" id="replay-list">${data.replays?.length ? `<div class="table-wrap"><table><thead><tr><th>Task</th><th>Token Change</th><th>Rework Change</th><th>Created</th></tr></thead><tbody>${data.replays.slice().reverse().map(replayRow).join("")}</tbody></table></div>` : empty("No replay receipts yet. Preview a comparison above.")}</div></div></div>`;
  const form = document.querySelector("#replay-form");
  document.querySelector("#preview-replay").addEventListener("click", async () => {
    try {
      clearError();
      const formData = new FormData(form);
      const task = String(formData.get("task") || "").trim();
      const cases = [readReplayCase(formData, "baseline", "baseline"), readReplayCase(formData, "assisted", "assisted")];
      pendingReplay = await api("/v1/replay", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "compare", task, cases }) });
      document.querySelector("#replay-result").innerHTML = replayResult(pendingReplay);
      document.querySelector("#save-replay").disabled = false;
    } catch (error) { showError(error); }
  });
  document.querySelector("#save-replay").addEventListener("click", async () => {
    if (!pendingReplay) return;
    try {
      clearError();
      await api("/v1/replay", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "save", replay: pendingReplay }) });
      showNotice("Replay evidence saved locally.");
      await renderReplay();
    } catch (error) { showError(error); }
  });
}

function replayRow(item) {
  const comparison = item.comparisons?.[0] || {};
  return `<tr><td>${esc(item.task)}</td><td>${esc(deltaText(comparison.token_delta, "Tokens"))}</td><td>${esc(deltaText(comparison.rework_delta, "Rework Attempts"))}</td><td class="muted">${esc(dash(item.created_at))}</td></tr>`;
}

async function renderDreaming() {
  const [data, records] = await Promise.all([api("/v1/dreams?owner=all"), api("/v1/records?limit=500")]);
  const owners = [...new Set((records.records || []).map((item) => item.owner).filter(Boolean))].sort();
  if (!owners.length) owners.push("human");
  const preferredOwner = owners.includes("studio-demo") ? "studio-demo" : owners.includes("human") ? "human" : owners.find((owner) => owner !== "shared") || owners[0];
  if (!owners.includes(dreamOwner)) dreamOwner = preferredOwner;
  const ownerOptions = owners.map((owner) => `<option value="${esc(owner)}"${owner === dreamOwner ? " selected" : ""}>${esc(owner === "shared" ? "Shared Memory" : owner)}</option>`).join("");
  view.innerHTML = `<div class="section"><div class="section-head dream-head"><div><h2>Dreaming</h2><p class="hint">Automatic consolidation creates candidates only. Nothing becomes trusted without evidence.</p></div><div class="dream-actions"><div class="toolbar"><label class="owner-picker"><span>Memory Scope</span><select id="dream-owner" title="Choose which owner's verified memories to analyze">${ownerOptions}</select></label><button class="button quiet" id="run-dream" title="Find relationships among verified memories">Find New Connections</button><button class="button" id="dream-demo">Load Guided Demo</button></div><p class="dream-help">Finds patterns across verified memories. New candidates still require evidence before promotion.</p></div></div><div class="panel" id="dream-list">${data.candidates?.length ? `<div class="table-wrap"><table><thead><tr><th>Candidate</th><th>Insight</th><th>Owner</th><th>State</th></tr></thead><tbody>${data.candidates.map((item) => `<tr><td>${esc(item.candidate_id)}</td><td>${esc(item.insight || item.reason || "Pattern candidate") }<br><span class="muted">${esc(item.source_experience_ids?.length || 0)} source experiences</span></td><td>${esc(dash(item.owner))}</td><td>${stateTag(item.status || "candidate")}</td></tr>`).join("")}</tbody></table></div>` : empty("No Dream candidates yet. Load the guided demo or complete two related verified tasks.")}</div></div>`;
  document.querySelector("#dream-owner").addEventListener("change", (event) => { dreamOwner = event.target.value; });
  document.querySelector("#run-dream").addEventListener("click", async (event) => {
    const button = event.currentTarget;
    try {
      clearError();
      button.disabled = true;
      button.textContent = "Finding Connections...";
      const result = await api("/v1/dream", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "run", agent_id: dreamOwner, max_candidates: 5 }) });
      const created = result.created?.length || 0;
      showNotice(created ? `Found ${created} new connection${created === 1 ? "" : "s"} for ${dreamOwner}.` : `No new connections found for ${dreamOwner}.`);
      await renderDreaming();
    } catch (error) {
      showError(error);
      button.disabled = false;
      button.textContent = "Run Dream Analysis";
    }
  });
  document.querySelector("#dream-demo").addEventListener("click", () => loadGuidedDemo(renderDreaming));
}

async function renderPolicy() {
  const data = await api("/v1/policy");
  view.innerHTML = `<div class="section">${sectionHeading("Policy", "The Memory Firewall decides what may enter, be retrieved, or leave local storage.")}
  <div class="panel panel-pad"><h3>Current Policy</h3><pre style="margin-top:10px">${esc(JSON.stringify(data.policy, null, 2))}</pre></div>
  <div class="section">${sectionHeading("Backups And Exports", "Create recoverable local copies without editing the store.")}<div class="panel panel-pad"><div class="toolbar"><button class="button" id="backup">Create Backup</button><button class="button quiet" id="export">Export JSON Snapshot</button><button class="button quiet" id="capsule">Export Capsule</button><span class="hint" id="portable-result"></span></div></div></div>
  <div class="section">${sectionHeading("Check An Input")}<div class="panel panel-pad"><form id="policy-form"><div class="form-grid"><label>Files (One Per Line)<textarea name="files" rows="4" placeholder="src/app.py\nconfig/.env"></textarea></label><label>Text To Inspect<textarea name="text" rows="4" placeholder="Summary or outcome text"></textarea></label></div><div class="form-actions"><button class="button" type="submit">Evaluate Admission</button></div></form><pre id="policy-result" style="margin-top:12px;display:none"></pre></div></div></div>`;
  const portable = document.querySelector("#portable-result");
  document.querySelector("#backup").addEventListener("click", async () => { try { const result = await api("/v1/storage/backup", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }); portable.textContent = `Backup Created At ${result.path}`; } catch (error) { showError(error); } });
  document.querySelector("#export").addEventListener("click", async () => { try { const result = await api("/v1/storage/export", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ approved: true }) }); portable.textContent = `Snapshot Exported To ${result.path}`; } catch (error) { showError(error); } });
  document.querySelector("#capsule").addEventListener("click", async () => { try { const result = await api("/v1/capsule", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "export", approved: true, owner: "human" }) }); portable.textContent = result.path ? `Capsule Exported To ${result.path}` : (result.reason || "Capsule export blocked"); } catch (error) { showError(error); } });
  document.querySelector("#policy-form").addEventListener("submit", async (event) => { event.preventDefault(); clearError(); const form = new FormData(event.currentTarget); try { const result = await api("/v1/policy/check", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ files: String(form.get("files")).split(/\r?\n/).filter(Boolean), text: String(form.get("text")).split(/\r?\n/).filter(Boolean) }) }); const target = document.querySelector("#policy-result"); target.style.display = "block"; target.textContent = JSON.stringify(result, null, 2); } catch (error) { showError(error); } });
}

const renderers = { home: renderHome, memories: renderMemories, evidence: renderEvidence, replay: renderReplay, dreaming: renderDreaming, policy: renderPolicy };
const titles = { home: "Overview", memories: "Memories", evidence: "Evidence", replay: "Replay Lab", dreaming: "Dreaming", policy: "Policy" };
async function navigate(next) { currentView = next; title.textContent = titles[next] || titleCase(next); document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === next)); clearError(); try { await renderers[next](); } catch (error) { showError(error); view.innerHTML = empty("This view could not load."); } }
document.querySelectorAll(".nav-item").forEach((item) => item.addEventListener("click", () => navigate(item.dataset.view)));

async function checkService() { try { const health = await api("/health"); status.textContent = health.ok ? "Local Service Healthy" : "Attention Required"; statusDot.className = "status-dot ok"; await navigate(currentView); } catch (error) { status.textContent = "Start MemCoder Service"; statusDot.className = "status-dot bad"; showError(new Error("The local service is not running. Start it with: memcoder service serve")); view.innerHTML = `<div class="section"><div class="panel panel-pad"><h2>Studio Is Ready</h2><p class="hint" style="margin-top:10px">The desktop shell is lightweight and local. Start the provider-free service, then press refresh.</p><div class="form-actions"><button class="button" id="retry">Retry Connection</button></div></div></div>`; document.querySelector("#retry")?.addEventListener("click", checkService); } }
checkService();
