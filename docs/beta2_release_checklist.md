# Beta 2.5 release checklist

This checklist prepares the Beta 2.5 pre-release. It is intentionally
stricter than a source-tree test pass: users install the wheel and configure a
host separately.

## Completed in this checkout

- [x] QA-gated Experience admission, reflection provenance, compact briefs,
  Skills, planning, plan audits, Skill health, and evaluation APIs implemented.
- [x] Provider-free regression suite passed without an external model provider.
- [x] Automatic Dream candidates, sandbox evidence, Cognition Contracts, and
  host certification checks implemented.
- [x] Dream candidates are included in portable snapshots and reversible
  rollback controls.
- [x] Clean source and wheel archive contents verified: release archives omit
  tests, controlled runs, local databases, build output, and auxiliary folders.
- [x] Package metadata and release notes prepared.
- [x] README updated with Codex, AGY, CLI, Python, privacy, architecture, and
  evidence guidance.

## Before committing

- [ ] Inspect `git status` and stage only source, docs, tests, and intended
  benchmark fixtures.
- [ ] Do **not** stage `chroma_db*`, `dist/`, `build/`, `.venv/`, local MCP
  config, `testing/beta2_controlled_runs/`, or `testing/beta2_evaluation_runs/`.
- [ ] Decide whether public benchmark fixtures belong in the repository. Never
  publish evaluator-only private verifiers if a future benchmark relies on them
  remaining unseen by the host agent.
- [ ] Review the README in GitHub's renderer; the animated hero and badges load
  from external public badge/image services.
- [ ] Run matched `baseline` / `dreaming` holdout evaluations and retain the
  candidate, sandbox, and promotion receipts.

## Before publishing to PyPI

- [ ] Remove any previous `build/`, `dist/`, and `memcoder.egg-info/` output so
  deleted packages cannot survive in a new wheel through stale build state.
- [ ] Run `python -m build --no-isolation`.
- [ ] In a new virtual environment, install the generated wheel and run
  `python -m memcoder --help`.
- [ ] Run `python -m memcoder setup-agy` in a disposable user configuration or
  verify its generated configuration before replacing a real host setup.
- [ ] Confirm the final version is unused on PyPI.
- [ ] Upload with a PyPI API token or Trusted Publisher—not an account password.

## Recommended release notes summary

> MemCoder Beta 2.5 adds automatic provider-free Dreaming, sandboxed candidate
> learning, deterministic Cognition Contracts, host certification, and matched
> Dreaming evaluation support while preserving QA-gated, reversible memory. The
> host model still solves and verifies tasks.
