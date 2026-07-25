# Beta 2 controlled transfer results

**Run date:** 2026-07-25  
**Host:** Antigravity CLI (AGY)  
**Agent ID:** `beta2-eval`

## Question tested

Can verified MemCoder experience and a promoted Skill help a host agent
generalize input-validation behavior beyond an intentionally incomplete public
test?

This is a narrow synthetic regression benchmark, not a claim of universal
coding improvement.

## Design

Two QA-approved seed fixes were used to promote the `Required field validation`
Skill. Each unseen holdout began from a clean fixture and was run in three
separate AGY conversations:

| Condition | Host guidance |
| --- | --- |
| Baseline | No MemCoder call. |
| Memory-guided | One `memcoder_prepare` call, with `include_skills: false`. |
| Skill-planned | One `memcoder_start` call, using the returned Skill-backed plan. |

Agents saw only the public test, which checks a missing key. After each agent
finished, the evaluator ran the private verifier. The private verifier also
checks null, whitespace-only, and non-string values. Holdout outcomes were not
recorded into MemCoder during the experiment, preventing cross-run leakage.

## Results

| Holdout | Baseline: public / private | Memory-guided: public / private | Skill-planned: public / private |
| --- | --- | --- | --- |
| `api_key` | Pass / Fail | Pass / Pass | Pass / Pass |
| `tenant_id` | Pass / Fail | Pass / Pass | Pass / Pass |
| `channel_name` | Pass / Fail | Pass / Pass | Pass / Pass |
| **Total** | **3 / 0 private passes** | **3 / 3 private passes** | **3 / 3 private passes** |

All three MemCoder-guided retrievals were relevant to the validation task.
Every condition made one focused edit after its initial public-test run. Token
usage was not captured consistently enough to report as a metric.

## Interpretation

For this matched validation family, the baseline agents fixed the visible
missing-key error but missed at least one private robustness case. Both
MemCoder-assisted conditions passed all private checks. This supports the
limited claim that the stored procedure transferred to these unseen variants.

It does **not** establish causality, quantify general performance gains, or
prove that the same effect will occur on unrelated tasks, models, or hosts.
The next evaluation should add realistic repository tasks, more task families,
and consistent guidance-token and rework measurements.
