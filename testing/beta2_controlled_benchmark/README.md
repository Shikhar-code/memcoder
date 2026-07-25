# Beta 2 controlled transfer benchmark

This synthetic benchmark measures one narrow claim: whether a Skill promoted
from verified seed experiences transfers broader input-validation behavior to an
unseen task.

Each public task asks only for missing-key behavior. The private verifier,
which must not be shown to the host before it finishes, also checks null,
whitespace-only, and non-string inputs. This mirrors a public-test/holdout-test
regression evaluation.

Use the already-promoted `Required field validation` Skill under agent ID
`beta2-eval`. For every task create three clean copies: `baseline`,
`memory_guided`, and `skill_planned`. Agents run only the public test. After an
agent finishes, run the matching verifier from `testing/beta2_hidden_verifiers`
yourself.

Do not let AGY inspect the hidden verifier folder.
