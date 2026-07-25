# Beta 2 repository-style transfer pack

This pack is a controlled, multi-module extension of the earlier validation
benchmark. It resembles small application components rather than claiming to
be a real external repository.

Each public test checks a realistic missing-field regression and a normal
return value. The private verifiers additionally check null, whitespace-only,
and non-string input. Use the already promoted `Required field validation`
Skill for agent `beta2-eval`.

For each task, create three clean copies under `testing/beta2_controlled_runs`:
`baseline`, `memory_guided`, and `skill_planned`. Agents may run only the
public test in their current folder. The evaluator runs the matching verifier
from `testing/beta2_repository_style_hidden_verifiers` after AGY completes.

Do not record any holdout outcome until all conditions are complete.
