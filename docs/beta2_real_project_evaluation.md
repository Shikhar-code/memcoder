# Beta 2 real-project evaluation

## Purpose

The controlled transfer benchmark establishes a narrow mechanism: validated
MemCoder guidance transferred across unseen input-validation variants. This
protocol tests whether that mechanism is useful on normal repository work.

It must not be reported as complete until it is run against a real project.

## Evaluation target

Choose one repository that is not the MemCoder source tree. Use a stable
revision and a task type that has a focused automated check. A small service,
CLI, automation project, or RAG component is suitable; an end-to-end video
render is not suitable as the primary verifier because provider rate limits and
render timing introduce unrelated variance.

Use three task families from that repository:

| Family | Suitable task | Deterministic verifier |
| --- | --- | --- |
| Validation / boundary handling | Required input, parsing, or configuration edge case | Focused unit test |
| State / data transformation | Incorrect normalization, mapping, serialization, or filtering | Focused unit or integration test |
| Failure handling | Retry boundary, exception conversion, fallback, or error report | Focused unit or integration test |

Each task must be a genuine issue or a pre-written regression fixture whose
private assertions are not visible to the host agent. Do not fabricate all
tasks from the same one-line pattern.

## Fair-run rules

For every task, prepare three clean copies from the same repository revision:

1. **Baseline:** no MemCoder tool call.
2. **Memory-guided:** call `memcoder_prepare` exactly once with
   `include_skills: false`.
3. **Skill-planned:** call `memcoder_start` exactly once after a relevant
   QA-backed Skill has been promoted.

Keep the host model, permissions, fixed task prompt, time budget, and public
tests identical. Use a new AGY conversation for each condition. Do not record
holdout outcomes until all task conditions finish.

The evaluator, not the host, runs the private verifier after AGY completes.

## Required evidence per run

Record:

- repository revision and task ID;
- condition and AGY conversation ID;
- public verifier output before and after the edit;
- private verifier result;
- changed files;
- meaningful edit/test cycles after the first attempt;
- MemCoder retrieval relevance for assisted conditions;
- returned plan ID and Skill ID for skill-planned runs; and
- measured guidance tokens when the host exposes them.

Mark a run invalid rather than silently retrying if a folder is reused, a host
sees private assertions, a forbidden MemCoder tool is called, or task files
from a previous condition remain in the working copy.

## Decision rule

This stage is successful when at least three diverse holdouts have complete,
valid triads and the MemCoder-assisted conditions improve private-verifier pass
rate or reduce rework without irrelevant retrieval. Report all valid and
invalid runs. Do not combine these results with the synthetic benchmark into a
single universal pass rate.

## Recommended first target

Start with the repository that has the fastest deterministic test loop and no
paid API or rendering dependency. Once those results are complete, repeat one
task family in an automation or RAG repository to test a different host
context.
