# Changelog

All notable changes to MemCoder are documented here.

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

- Added the Beta 2.5 evaluation record, Dreaming holdout instructions, and an
  explicit boundary between provider-free safety evidence and pending host
  outcome evidence.

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
