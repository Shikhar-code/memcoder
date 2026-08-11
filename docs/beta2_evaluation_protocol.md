# MemCoder Beta 2 evaluation protocol

## Purpose

This protocol measures whether MemCoder improves a host agent's work. It does
not treat unit-test success as evidence of agent improvement.

The comparison has four conditions for the same task:

1. `baseline` — the host receives the task and project only. It must not call
   MemCoder.
2. `memory_guided` — the host calls `memcoder_prepare` once with
   `include_skills: false`, then uses the returned brief without a promoted
   Skill procedure.
3. `skill_planned` — the host calls `memcoder_start` after a relevant Skill has
   been promoted, then follows the returned plan.
4. `dreaming` — the host uses automatic Dream candidates generated from prior
   verified seed work and sandbox-checked before use.

## Before running any task

- Choose 10–20 realistic tasks from one project or a tightly related set of
  projects. At least 6 must be unseen holdout tasks.
- Every task must have one focused, deterministic verification command.
- Write the expected behavior before any condition is run.
- Use a clean copy or clean worktree per task-condition run. Never reuse files
  modified by a previous condition.
- Use a separate host conversation/session for each condition. Baseline hosts
  must not be given past solution text, generated Skills, or MemCoder output.
- Keep the model, model settings, task prompt, permissions, and time budget the
  same across all four conditions.

## Seeding and Skill promotion

Run two completed, QA-approved seed tasks that share a real procedure. Record
their returned Experience IDs. Promote exactly one Skill from those IDs. Record
the Skill ID in the manifest.

Do not promote a Skill from the holdout tasks before they have been evaluated.

## Per-run workflow

1. Copy the task fixture or check out a clean worktree.
2. Give the host the fixed task prompt from the manifest.
3. For `memory_guided`, call `memcoder_prepare` once with
   `include_skills: false`. For `skill_planned`, call `memcoder_start` once.
4. For `skill_planned`, preserve the returned `plan.id` and source Skill ID.
5. For `dreaming`, preserve the candidate ID, sandbox checks, and promoted
   record ID if promotion occurred. An unchecked candidate stays outside
   trusted retrieval.
6. Require the host to run the manifest's verification command once before
   editing and once after editing. This makes retry/rework counts comparable.
7. Record the observed result, rework count, retrieval relevance, and guidance
   token estimate in `eval/beta2_runs.json`.
8. Do **not** call `memcoder_record` for any holdout until every condition for
   every holdout is complete. Immediate recording could expose an exact holdout
   Experience to a later run and invalidate the comparison.
9. After the comparison is complete, record the verified MemCoder-condition
   outcomes with their captured plan/Skill identifiers so audits and Skill
   health can update outside the experiment.

## Required measurements

| Field | Rule |
| --- | --- |
| `passed` | True only when the predetermined verification command passes. |
| `rework_count` | Number of meaningful retry/edit/test cycles after the first attempt. |
| `retrieval_relevant` | Required for MemCoder conditions; true only if guidance addressed the actual task. |
| `guidance_tokens` | Optional host-observed or estimated tokens injected from MemCoder. |
| `notes` | Optional concise observation; never used as a metric. |

## Decision rule

Use `memcoder evaluate --input eval/beta2_runs.json` only after all matched
runs are complete. Beta 2.5 needs evidence that, on matched holdouts,
`dreaming` improves pass rate or lowers rework without unacceptable negative
transfer, memory pollution, retrieval irrelevance, or token cost.

If a Skill creates repeated failures, retain the plan audits and allow Skill
health to mark it `review_required`; do not silently delete unfavorable runs.

## What this protocol cannot prove

- It cannot establish causality from a small sample.
- It cannot replace human review of task quality.
- It does not measure visual or product quality unless the host's verification
  command measures it.
