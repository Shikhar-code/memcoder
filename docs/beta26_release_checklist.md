# Beta 2.6 release checklist

This checklist prepares the 0.2.6b1 source release. It covers the new
Failure Frontier, causal calibration, and Cognitive Branch surfaces without
claiming that the provider-free Core is universally intelligent.

## Completed in this checkout

- [x] Failure Frontier records, applicability matching, explicit feedback, and
  Autopilot surfacing.
- [x] Utility feedback calibration summaries with bounded recommendations.
- [x] Cognitive Branch changes, proof obligations, deterministic diffs,
  conflict detection, merge gates, and reversible rollback.
- [x] Python, CLI, MCP, snapshot, and Codex-plugin surfaces updated.
- [x] Focused Beta 2.6 tests pass without an external provider.

## Before committing

- [ ] Inspect `git status` and stage only the intended source, docs, tests, and
  plugin files.
- [ ] Run the focused Beta 2.6 tests and the provider-free regression list in
  `AGENTS.md`.
- [ ] Verify branch merge refuses incomplete proof, conflicts, and environment
  drift; verify rollback preserves the branch manifest.
- [ ] Verify `memcoder storage export` and `storage restore` preserve frontiers
  and branches without deleting local state.
- [ ] Do not stage local databases, `.venv/`, `dist/`, `build/`, or host config.

## Before publishing

- [ ] Build a clean 0.2.6b1 wheel from a fresh checkout.
- [ ] Install the wheel in a disposable environment and run
  `python -m memcoder --help`.
- [ ] Refresh/reinstall the Codex plugin so its 0.2.6 manifest and skill are
  loaded.
- [ ] Run a matched real-project evaluation for failure prevention,
  calibration, negative transfer, merge safety, token use, and rollback.
