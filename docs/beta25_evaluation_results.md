# Beta 2.5 evaluation record

**Run date:** 2026-08-11  
**Scope:** provider-free implementation and safety evidence in this checkout

## What was actually verified

The provider-free Beta 2.5 checks passed, including:

- automatic Dream candidate creation after a QA-approved outcome;
- sandbox evidence requirements and rejection of malformed evidence;
- promotion only after proof and reversible rollback;
- Cognition Contract rules and host certification privacy checks;
- CLI exposure for `dream`, `contract`, and `host-certify`;
- Dream-candidate snapshot and restore behavior; and
- the existing Beta 2 regression suite (20 targeted tests) plus bytecode
  compilation.

These checks establish that the new lifecycle is bounded, evidence-gated,
provider-free, and reversible. They do not establish that an arbitrary host
agent writes better code.

## Matched baseline versus Dreaming status

**Status: pending.** A valid host-outcome comparison was not run in this
checkout. The repository's `eval/beta2_task_manifest.json` is still a template,
and there are no paired baseline/Dreaming host receipts, clean worktree IDs,
conversation IDs, or measured rework/token records to evaluate. The existing
`eval/beta2_runs.json` contains the earlier baseline, memory-guided, and
skill-planned transfer data, but no Dreaming rows.

It would be misleading to manufacture Dreaming pass/fail results from unit
tests, so the release gate remains open until a host runs the same unseen tasks
with and without automatic Dreaming under the protocol.

## Required next evidence

1. Fill the task manifest with at least six unseen, deterministic holdouts.
2. Run clean, matched `baseline` and `dreaming` host sessions with the same
   model, permissions, prompt, and time budget.
3. Retain candidate IDs, sandbox checks, promotion/rollback receipts, public
   and private verifier output, rework counts, retrieval relevance, and token
   estimates.
4. Run `memcoder evaluate --input eval/beta2_runs.json` and publish the report
   beside this record.

Until those runs exist, Beta 2.5 is implementation-ready but not evidence-
complete for a claim of general developer quality improvement.
