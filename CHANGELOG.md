# Changelog

All notable changes to MemCoder are documented here.

## 0.3.3b1 — Beta 3.3

### Added

- Added explicit host outcome normalization for intervention use, changed
  action, verification, rework, and token measurements.
- Added prediction receipts that close exactly once at verification and remain
  privacy-safe by storing proof summaries rather than raw evidence.
- Added bounded environment-aware outcome calibration and strict host checks for
  outcome closure and prediction receipts.
- Added closed-loop outcome summaries to the local service and lightweight
  Studio evidence view.
- Added deterministic proof-loop regression coverage.

### Changed

- Autopilot now connects prior intervention receipts to later verification
  events even when the host's task wording changes slightly.
- Ambiguous outcomes remain unmeasured; passing work alone never implies that
  retrieved guidance was helpful.
- Package, Studio, Codex plugin, and Claude bundle metadata now identify
  `0.3.3b1` / Beta 3.3.

### Boundary

- Beta 3.3 remains local, provider-free, fail-open, and single-user. It does
  not add cloud sync, team cognition, multi-agent coordination, or automatic
  mutation of trusted memories.

## 0.3.2b1 — Beta 3.2

### Added

- Added a versioned provider-free host manifest for Codex, AGY, and Claude Code.
- Added strict host certification for schema, identity, event IDs, token
  budgets, QA admission, privacy, and fail-open receipts.
- Added `memcoder setup-claude`, Claude Code MCP configuration, and an
  idempotent `CLAUDE.md` lifecycle block.
- Added `memcoder host-manifest` and host-aware `memcoder doctor` diagnostics.
- Added a portable Claude Code skill and MCP example under `plugins/claude/`.
- Added deterministic Beta 3.2 host-parity fixtures and setup tests.

### Changed

- AGY setup now preserves other servers, backs up changed configuration, and
  remains safe to rerun.
- Codex, AGY, and Claude documentation now describe the same Autopilot lifecycle
  and provider-free trust boundary.
- Package, Studio, and Codex plugin metadata are aligned to `0.3.2`.

### Boundary

- Beta 3.2 does not add cloud sync, team memory, multi-agent cognition, or
  provider-powered intelligence.

## 0.3.1b1 — Beta 3.1

### Changed

- Deferred semantic-index initialization until retrieval or an approved
  Markdown import actually needs it, reducing MCP import startup to about three
  seconds on the Windows development host.
- Enforced host-declared cognition token budgets, including final packet
  metadata and Failure Frontier additions; undersized budgets now abstain.
- Withheld archetype-only retrieval matches unless action-specific overlap or a
  verified environment match supports transfer.
- Normalized common diagnostic and boolean-pass verification evidence while
  preserving inspectable-proof requirements and actionable QA rejection detail.
- Made repeated completion lifecycle events reuse the original capture instead
  of learning twice after retries or restarts.

### Host integration

- Refreshed the Codex plugin metadata for Beta 3.1 and retained explicit MCP
  startup and tool timeouts.
- Kept AGY / Antigravity and Claude Code parity as required pre-1.0 host gates.

## 0.3.0b1 — Beta 3.0

### Added

- Added the local Memory Firewall with explainable admission rules, secret and
  sensitive-path blocking, policy persistence, and provider-free diagnostics.
- Added an idempotent append-only host event journal for local adapter and Studio
  integrations; journal failures never block lifecycle cognition.
- Added deterministic Cognition Replay comparisons for baseline, memory-assisted,
  token, rework, and verification outcomes.
- Added checksummed Cognition Capsules with owner filtering, provenance-preserving
  inspection, verification, dry-run import, and reviewed restore.
- Added a standard-library localhost service with health, doctor, policy-check,
  records, evidence, policy, replay, storage, and fail-open Autopilot endpoints.
- Added a lightweight Tauri desktop Memory Studio with Overview, Memories,
  Evidence, Replay Lab, Dreaming, and Policy views. It has no frontend framework,
  charting dependency, or duplicate memory engine.
- Added `memcoder setup`, `doctor`, `policy`, `replay`, and `capsule` CLI surfaces,
  plus corresponding Python API entry points.

### Changed

- Lifecycle receipts are mirrored into the event journal without changing the
  existing Autopilot storage contract.
- Memory admission now applies the local policy before QA-approved records are
  persisted.
- Package metadata and public documentation now identify Beta 3.0 (`0.3.0b1`).

## 0.2.6b1 — Beta 2.6

### Added

- Added a provider-free Failure Frontier that records observed triggers,
  risks, verification obligations, counterexamples, and calibrated outcomes
  without promoting warnings into trusted memory.
- Added causal utility summaries so helpful, ignored, misleading, and harmful
  intervention outcomes produce an inspectable calibration signal.
- Added reversible Cognitive Branches for hypotheses, branch-local changes,
  deterministic Cognitive Diffs, proof obligations, conflict detection, and
  merge/rollback gates.
- Exposed Beta 2.6 through the Python API, CLI, MCP server, portable snapshots,
  and the local Codex plugin.

### Changed

- Lifecycle Autopilot now surfaces applicable Failure Frontier warnings and can
  record host-supplied failure-frontier evidence fail-open.
- Branch and frontier state remain append-only and owner-scoped; no trusted
  memory is silently overwritten or deleted.

## 0.2.5b1 — Beta 2.5

### Added

- Added automatic provider-free Dreaming after QA-approved work. It proposes
  local candidates from verified episodes without requiring a manual trigger.
- Added sandbox evidence checks and reversible promotion into Principles;
  candidates never enter trusted retrieval while unverified.
- Added deterministic Cognition Contracts and host certification checks for
  lifecycle, QA-gated learning, and fail-open behavior.
- Added a `dreaming` evaluation condition for matched baseline experiments.
- Exposed Dreaming, Cognition Contracts, and host certification through Python,
  CLI, MCP, and the Codex plugin.

### Changed

- Beta 2.5 keeps trusted memory immutable until candidate evidence passes its
  sandbox gate; high-impact changes remain inspectable and reversible.

### Documentation

- Added Dreaming holdout instructions and an explicit boundary between
  provider-free safety evidence and future host-outcome evidence.

## 0.2.4b1 — Beta 2.4

### Added

- Added a provider-neutral lifecycle autopilot with attention deduplication,
  fail-open execution, pause/inspect/resume/rollback controls, and reversible
  QA-gated capture.
- Added prospective failure radar, risk-scaled verification planning, and a
  lifecycle token ledger.
- Added versioned Skill contracts, explicit safe-transfer compilation,
  composition conflict detection, project overlays, and causal influence credit.
- Exposed Beta 2.4 through Python, CLI, MCP, and the local Codex plugin.

### Changed

- Codex can now invoke one automatic lifecycle entry point instead of requiring
  users to write MemCoder-specific prompts.
- Skill health can distinguish a Skill that changed behavior from one that was
  merely present.

## 0.2.3b1 — Beta 2.3

### Added

- Added decision framing, utility-aware ranking and vetoes, diverse evidence,
  intervention receipts, exact-intervention feedback, and retrieval diagnostics.
- Added Project Cortex with bounded project state, rationale-bearing decisions,
  environment-drift invalidation, Project Resurrection, and secret-scrubbed
  cross-host handoff capsules.
- Exposed Beta 2.3 through Python, CLI, MCP, and the local Codex plugin.

### Changed

- Trusted semantic matches must now also clear a decision-utility gate before
  they can influence the host.
- Updated the Codex workflow to preserve material project state and report
  whether retrieved guidance actually helped.

## 0.2.2b1 — Beta 2.2

### Added

- Added the first provider-free cognitive runtime with bounded intervention,
  Transfer Delta, belief separation, falsifiable predictions, reuse checks, and
  owner-scoped task checkpoints.
- Added a local Codex desktop plugin bundle, plus an environment-binding setup
  script, that invokes MemCoder implicitly for substantive development work.

### Changed

- Rebuilt the README around a clearer product story, host-specific onboarding,
  the cognitive runtime, trust boundaries, and current evidence limits.

### Removed

- Retired the disconnected Alpha agent/client/server stack, Ollama workflows,
  exploratory LLM extraction utilities, and obsolete Beta-1 proof fixtures.
- Replaced the legacy `MemCoderAgent` SDK export with the current provider-free
  cognition API.

## 0.2.0b1 — Beta 2 release candidate

### Added

- QA evidence gate for outcome admission, with `verify` available through the
  CLI, Python API, and MCP.
- Compact, token-bounded cognition briefs and a one-call `start` operation.
- Evidence-backed Skill promotion, deterministic bounded planning, plan audit
  history, and derived Skill health.
- Explicit baseline / memory-guided / skill-planned evaluation reporting.
- Reflection provenance back to the QA-approved Experience that produced it.
- `include_skills: false` retrieval control for memory-only evaluation or host
  workflows.
- Controlled transfer evaluation results and a real-project evaluation protocol.
- Source distribution controls that exclude local tests, runs, build products,
  and auxiliary project material from release archives.

### Changed

- Reworked the README into a product-oriented installation, host-integration,
  privacy, evaluation, and AGY usage guide.
- Refined the reliable AGY workflow: retrieve MemCoder guidance in a dedicated
  first interaction, then give the host the task in the same conversation.

### Compatibility

- The provider-free MCP and CLI workflows do not require Ollama, CUDA, an API
  key, or a local generation server.

### Evidence boundary

- Beta 2 has controlled evidence of validation-procedure transfer. It is a
  pre-release and does not claim general coding improvement across repositories
  or hosts. See [controlled transfer results](docs/beta2_controlled_transfer_results.md).
