# Changelog

All notable changes to MemCoder are documented here.

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
- Legacy Ollama helpers remain optional through `memcoder[ollama]`.

### Evidence boundary

- Beta 2 has controlled evidence of validation-procedure transfer. It is a
  pre-release and does not claim general coding improvement across repositories
  or hosts. See [controlled transfer results](docs/beta2_controlled_transfer_results.md).
