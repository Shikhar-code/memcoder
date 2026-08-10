# Changelog

All notable changes to MemCoder are documented here.

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
