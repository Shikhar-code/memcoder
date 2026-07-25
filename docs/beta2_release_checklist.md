# Beta 2 release checklist

This checklist prepares the `0.2.0b1` Beta 2 pre-release. It is intentionally
stricter than a source-tree test pass: users install the wheel and configure a
host separately.

## Completed in this checkout

- [x] QA-gated Experience admission, reflection provenance, compact briefs,
  Skills, planning, plan audits, Skill health, and evaluation APIs implemented.
- [x] Provider-free local test suite passed (24 tests; the legacy Alpha test is
  excluded because it depends on external embedding-model availability).
- [x] Clean source and wheel archive contents verified: release archives omit
  tests, controlled runs, local databases, build output, and auxiliary folders.
- [x] `0.2.0b1` metadata and release notes prepared.
- [x] README updated with installation, CLI, AGY, privacy, and evidence guidance.

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

## Before publishing to PyPI

- [ ] Run `python -m build --no-isolation`.
- [ ] In a new virtual environment, install the generated wheel and run
  `python -m memcoder --help`.
- [ ] Run `python -m memcoder setup-agy` in a disposable user configuration or
  verify its generated configuration before replacing a real host setup.
- [ ] Confirm the final version is unused on PyPI.
- [ ] Upload with a PyPI API token or Trusted Publisher—not an account password.

## Recommended release notes summary

> MemCoder 0.2.0b1 adds evidence-gated learning, compact cognition briefs,
> reusable Skills, bounded plans, plan audits, Skill health, and explicit
> evaluation reporting. It remains a provider-independent, local-first
> cognition layer: the host model still solves and verifies tasks.
