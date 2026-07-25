# Beta 2 controlled AGY evaluation pack

This pack is for the real-agent portion of the Beta 2 evaluation. Every task
starts intentionally failing. Do not run the task folders in place: copy a
fresh task folder for every condition.

## Task order

1. Complete `seed_service_name` and `seed_deployment_name` with MemCoder
   recording enabled under the stable agent ID `beta2-eval`.
2. Promote one Skill from the two returned Experience IDs.
3. Evaluate every holdout task under each condition:
   `baseline`, `memory_guided`, and `skill_planned`.

## Fixed prompts

Replace `<TASK_DIR>` with the copied task folder and `<TEST_COMMAND>` with its
listed test command. Keep all other wording unchanged.

### Baseline

```text
Work only inside <TASK_DIR>. Do not read or modify any MemCoder source files,
documentation, or memory database. Fix the failing public test using the
smallest correct change. Run <TEST_COMMAND>. Report the changed file and the
complete test output.
```

### Memory-guided

```text
Work only inside <TASK_DIR>. Do not read or modify any MemCoder source files,
documentation, or memory database. Before investigating, call memcoder_prepare
exactly once with the task problem, agent_id "beta2-eval", and
include_skills false. Use returned guidance as a hypothesis, not proof. Do not
inspect MemCoder implementation.
Fix the failing public test using the smallest correct change. Run
<TEST_COMMAND>. Do not call memcoder_record yet; holdout recording is deferred
until every evaluation condition is complete. Report the changed file, complete
test output, and MemCoder output.
```

### Skill-planned

```text
Work only inside <TASK_DIR>. Do not read or modify any MemCoder source files,
documentation, or memory database. Before investigating, call memcoder_start
exactly once with the task problem and agent_id "beta2-eval". Follow its plan
only while it fits the current task; do not inspect MemCoder implementation.
Fix the failing public test using the smallest correct change. Run
<TEST_COMMAND>. Do not call memcoder_record yet; holdout recording is deferred
until every evaluation condition is complete. Preserve the returned plan.id and
source Skill ID. Report the changed file, complete test output, and MemCoder
output.
```

## Commands

| Task | Test command |
| --- | --- |
| `seed_service_name` | `python test_service_name.py` |
| `seed_deployment_name` | `python test_deployment_name.py` |
| `holdout_worker_id` | `python test_worker_id.py` |
| `holdout_profile_email` | `python test_profile_email.py` |
| `holdout_batch_job_id` | `python test_batch_job_id.py` |
| `holdout_environment_name` | `python test_environment_name.py` |

Record every completed run in `eval/beta2_runs.json` according to
`docs/beta2_evaluation_protocol.md`.

For every holdout condition, instruct the host to run the listed test once
before editing and once after editing. Use the same sequence in every
condition.
