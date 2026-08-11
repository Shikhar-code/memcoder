# MemCoder product and research roadmap

**Current line:** Beta 2.4<br>
**North star:** the dependable cognition layer for long-lived AI agents<br>
**Last revised:** 2026-08-11

> MemCoder should not merely help an agent remember. It should help the agent
> notice what matters, recover verified project state, transfer prior learning
> safely, avoid repeated failures, spend fewer tokens, and improve from evidence
> without becoming opaque or provider-dependent.

---

## Executive thesis

AI agents are increasingly capable inside one task and surprisingly forgetful
across tasks. Existing memory systems usually solve this by storing transcripts,
summaries, or vectors and injecting whatever appears semantically similar. That
creates three predictable failures:

1. **Similarity is mistaken for usefulness.** A memory can be relevant in topic
   and still be useless—or harmful—for the current decision.
2. **Claims become memory before they become knowledge.** Raw model output,
   unsupported conclusions, and stale solutions can silently compound.
3. **Memory increases context instead of reducing it.** The agent receives more
   text but not necessarily a better next action.

MemCoder's position is different:

```text
Memory is not stored context.
Memory is verified evidence that can change a future decision safely.
```

The finished product should behave like an invisible project cortex:

```text
normal developer request
→ understand the decision and risk
→ stay silent or surface the smallest useful cognition
→ help the host act and verify
→ learn only from admitted evidence
→ improve the next related decision
```

This roadmap is intentionally ambitious. It is also sequential. MemCoder should
not build Dreaming, cloud coordination, or an impressive GUI on top of retrieval
that still surfaces valid-but-useless memories.

---

## The product promise

A developer installs MemCoder once. From that point onward, compatible agents
should:

- remember verified decisions and outcomes across sessions;
- recover project state without replaying long conversations;
- surface prior failures before repeating them;
- distinguish facts, hypotheses, assumptions, and stale knowledge;
- adapt a prior solution to the current environment instead of copying it;
- propose the cheapest credible verification path;
- reuse proven procedures through versioned Skills;
- consume less context than they save;
- explain every intervention and allow the developer to undo it; and
- continue working normally when MemCoder has nothing useful or is unavailable.

The developer should not need to know a tool name, construct memory payloads, or
write a special prompt for ordinary use.

---

## What “true cognition” means here

MemCoder will not claim consciousness, human reasoning, or unrestricted
self-modification. “Cognition” has an operational meaning:

| Cognitive capability | MemCoder interpretation |
| --- | --- |
| **Attention** | Decide whether prior knowledge deserves attention now. |
| **Situation awareness** | Maintain a bounded model of current project state, constraints, decisions, and uncertainty. |
| **Memory** | Preserve evidence-backed episodes, observations, principles, procedures, and failures. |
| **Transfer** | Compute what safely carries from past evidence into the current environment. |
| **Planning** | Apply trusted Skills as bounded, testable procedures. |
| **Metacognition** | Track confidence, assumptions, expected value, and why an intervention occurred. |
| **Verification** | Select proof proportional to risk and refuse unsupported learning. |
| **Consolidation** | Derive candidate patterns, counterexamples, and hypotheses from accumulated evidence. |
| **Self-correction** | Update validity, confidence, Skill health, and retrieval policy from verified outcomes. |

This definition is deliberately testable. If a feature cannot change a decision,
reduce a risk, improve verification, restore state, or save work, it does not
count as cognition merely because it uses an intelligent-sounding label.

---

## The target cognitive architecture

MemCoder evolves through eight connected layers.

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 8. Control plane                                                    │
│    Studio · policies · privacy · sync · audit · rollback            │
├─────────────────────────────────────────────────────────────────────┤
│ 7. Consolidation                                                    │
│    Dreaming · replay · counterexamples · hypotheses · calibration   │
├─────────────────────────────────────────────────────────────────────┤
│ 6. Verification intelligence                                        │
│    proof planning · Failure Radar · evidence admission · drift      │
├─────────────────────────────────────────────────────────────────────┤
│ 5. Procedural intelligence                                          │
│    Skills · composition · bounded plans · health · rollback         │
├─────────────────────────────────────────────────────────────────────┤
│ 4. Transfer intelligence                                            │
│    safe delta · applicability · causal evidence · counterfactuals   │
├─────────────────────────────────────────────────────────────────────┤
│ 3. Attention governor                                               │
│    utility · abstention · token budget · intervention policy        │
├─────────────────────────────────────────────────────────────────────┤
│ 2. Situation model                                                  │
│    project state · decisions · constraints · open loops · beliefs   │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Evidence substrate                                               │
│    records · provenance · validity · ownership · migrations         │
└─────────────────────────────────────────────────────────────────────┘
```

The provider-free Core must remain useful through all eight layers. Optional
models may later strengthen semantic synthesis, simulation, and critique, but
they cannot become an undeclared requirement for basic correctness.

---

## Memory model

The existing hierarchy remains sound, but each layer gains stricter semantics.

```text
Experience
├─ Reflection
├─ Mistake / risk
└─ Principle
   └─ Skill
      └─ Plan
```

| Layer | Durable meaning | Admission boundary |
| --- | --- | --- |
| **Experience** | A task, action, environment, evidence, and verified outcome. | Host evidence passed QA. |
| **Reflection** | A concise observation about the investigation or reasoning process. | Derived from an approved Experience. |
| **Mistake / risk** | A verified failure mode, bad assumption, or negative outcome. | Failure evidence is inspectable. |
| **Principle** | Transferable guidance supported by one or more Experiences. | Applicability and counterexamples are explicit. |
| **Skill** | A versioned procedure with preconditions, steps, proof, failure handling, and rollback. | Supporting evidence and promotion rules pass. |
| **Plan** | A bounded application of a Skill to the present task. | Assumptions fit the current situation model. |

Three additional structures sit beside semantic memory:

- **Task checkpoints:** temporary working state; never automatically promoted.
- **Decision records:** choice, rationale, rejected alternatives, validity
  conditions, and evidence.
- **Audit events:** append-only operational history; never retrieved as guidance
  merely because it exists.

---

## Non-negotiable product principles

1. **Evidence before durable learning.** No passing proof, no trusted memory.
2. **Correct abstention is success.** Silence is better than weak cognition.
3. **Guidance is never authority.** The host verifies the current project.
4. **Local-first Core.** Cloud and provider intelligence remain optional.
5. **Minimum sufficient cognition.** Return the smallest packet that changes the
   next action safely.
6. **Provenance over mystique.** Every derived claim must expose its support.
7. **Validity is temporal.** Memories can become stale when their environment
   changes.
8. **Negative evidence matters.** Failed approaches and counterexamples are not
   second-class memories.
9. **Automation must degrade safely.** A MemCoder failure must not block the
   host's normal workflow.
10. **Everything important is reversible.** Imports, promotions, consolidation,
    sync, and automatic learning need preview, history, and rollback.

---

## Honest current assessment

### What MemCoder already does well

- Provider-free persistent memory with owner isolation.
- Confidence- and validity-gated retrieval.
- QA admission for verified outcomes.
- Provenance, contradiction, retention, backup, export, and restore.
- Evidence-backed Principles, Skills, bounded plans, and Skill health.
- Compact cognition packets with `none`, `risk`, `brief`, and `plan` modes.
- Task checkpoints outside the semantic guidance index.
- CLI, Python, MCP, AGY, and local Codex Desktop integration paths.
- Narrow controlled evidence that verified procedures can transfer to unseen
  task variants.

### What it does not yet do well enough

- Distinguish semantic similarity from decision utility consistently.
- Learn whether an intervention actually helped, was ignored, or caused harm.
- Maintain a dependable current model of a repository or project.
- Resume a project from compact verified state.
- Intervene automatically at all useful host lifecycle boundaries.
- Demonstrate net token savings after including its own overhead.
- Prevent repeated failures before action, rather than explaining them later.
- Evolve or compose Skills with strong counterexample testing.
- Consolidate memories offline without manual orchestration.
- Offer a polished inspection and correction interface.
- Demonstrate broad, repeatable improvement on real repositories.

### Current product verdict

MemCoder is a credible verification-first memory and procedural-learning layer.
It is not yet a proven cognitive multiplier. If it vanished today, a strong
agent could still complete many tasks with little immediate loss. The roadmap's
job is to make that statement false through measurable developer outcomes—not
through more terminology.

---

## The 9/10 developer bar

The following are release gates, not current claims.

| Dimension | 9/10 target | How it is measured |
| --- | --- | --- |
| **Retrieval precision** | At least 90% precision at the first surfaced item on diverse held-out developer tasks. | Human-labelled and hidden-task retrieval set. |
| **Correct abstention** | At least 90% of no-memory tasks receive no automatic guidance. | Negative and out-of-domain task set. |
| **Intervention quality** | At least 95% helpful or correctly silent; fewer than 1% harmful. | Explicit host feedback plus outcome review. |
| **Correctness** | No reduction in pass rate or hidden-check correctness versus the same host without MemCoder. | Matched baseline and assisted runs. |
| **Failure prevention** | Repeated known failure families are intercepted before the bad action in at least 80% of eligible cases. | Failure Radar replay suite. |
| **Developer effort** | At least 20% less repeated investigation, rework, or unnecessary tool use. | Real-repository task traces. |
| **Token dividend** | At least 15% median net token reduction after counting retrieval and injected context. | End-to-end token ledger. |
| **Continuity** | A fresh host can recover the correct project state and next action from a bounded brief in at least 90% of handoff tasks. | Session-resurrection benchmark. |
| **Onboarding** | Supported host setup completes in under two minutes with ordinary prompts afterward. | Clean-machine installation trials. |
| **Reliability** | Autopilot failures fall back to normal host behavior; no user data loss. | Fault-injection and migration tests. |
| **Explainability** | Every intervention exposes trigger, evidence, applicability, expected benefit, risk, and proof. | Contract tests and UI audit. |

A 9/10 is not “many features.” It is a product developers miss when it is
disabled.

---

## Release map at a glance

| Release | Product outcome | Defining gate |
| --- | --- | --- |
| **Alpha** | Persistent semantic memory foundation. | Store and retrieve owner-scoped memory. |
| **Beta 1–1.2** | Provider-free, verified memory that other hosts can use. | Safe admission, transfer proof, and practical installation. |
| **Beta 2.0–2.2** | Skills, plans, durable evidence, and first cognitive runtime. | Bounded intervention with QA-backed learning. |
| **Beta 2.3** | Utility Engine plus Project Cortex. | Useful retrieval, strong abstention, and correct state recovery across sessions. |
| **Beta 2.4** | Invisible Autopilot, token economy, and Skill Intelligence. | Ordinary prompts, measurable savings, failure prevention, and dependable procedural transfer. |
| **Beta 2.5** | Dreaming, evaluation, and Core hardening. | Candidate learning survives adversarial checks and the complete system meets the 9/10 bar. |
| **Beta 3** | Memory Studio, cloud continuity, optional Intelligence, and later collective cognition. | Developers can inspect and control cognition; optional product layers preserve Core's trust and privacy boundaries. |
| **RC** | Promise and contract freeze. | No data-loss, privacy, migration, or silent-learning blocker. |
| **Core 1.0** | Dependable local cognition layer. | Stable product claim backed by reproducible real-project evidence. |

---

# Completed foundation

## Alpha — Semantic memory foundation — complete

**Purpose:** prove persistent memory and explore a cognitive hierarchy.

### Established

- Persistent semantic storage.
- Experience, Reflection, Principle, and Mistake concepts.
- Owner-scoped retrieval.
- Early reflection and autonomous-learning experiments.
- Early Ollama and Qwen-backed experiments.

### Lessons

- Storage without quality admission creates pollution.
- Similarity search alone does not create safe transfer.
- Provider dependence harms installation and portability.
- Reflection text is not evidence of changed behavior.

The provider-bound experimental paths are historical context, not current Core
architecture.

---

## Beta 1 — Provider-free verified memory — complete

**Purpose:** make memory-assisted work safe enough to test seriously.

### Delivered

- Provider-free CLI and MCP operation.
- Confidence-gated retrieval and owner isolation.
- Controlled shared-memory retrieval.
- Memory quality filtering and reflection validation.
- Markdown instruction import with preview and approval.
- AGY transfer proof on a related unseen validation task.

### Proven boundary

MemCoder could store a verified outcome and later help a related task. The
evidence was narrow and did not prove general improvement.

---

## Beta 1.1 and 1.2 — Adoption and host independence — complete

### Delivered

- PyPI packaging and simpler installation.
- `memcoder setup-agy` onboarding.
- Markdown import by file path.
- Provider-neutral CLI and Python integration boundaries.
- Documentation and host prompt templates.

### Lessons

- Requiring elaborate prompts is not automation.
- Host integration must bind to the correct Python environment reliably.
- A plugin that users must constantly remember to invoke is not yet a catalyst.

---

## Beta 2.0 — Verified Skills and bounded plans — complete

**Release:** `0.2.0b1`

### Delivered

- Structured QA admission.
- Compact cognition briefs.
- Evidence-backed Skill promotion.
- Bounded Skill-guided plans.
- Plan audits and derived Skill health.
- Reflection provenance.
- Baseline, memory-guided, and skill-planned evaluation reporting.
- Controlled evidence that valid assisted runs passed hidden robustness checks
  where matched visible-test baselines failed.

### Lessons

- Procedures transfer better than isolated snippets.
- Plans require assumptions, proof, and replan conditions.
- Passing a visible test is not enough evidence of robust learning.

---

## Beta 2.1 — Durable evidence substrate — complete

### Delivered

- Stable record IDs, schema versions, revisions, and lifecycle states.
- Durable records separated from the rebuildable vector index.
- Append-only plan audit history.
- Typed provenance edges and legacy backfill.
- Environment-aware validity and retrieval penalties.
- Proof-carrying memory and verification playbooks.
- Storage status, migration, export, backup, restore, and index rebuild.
- Evidence-preserving retention and contradiction workflows.
- Per-user data storage outside package files.

### Remaining refinements

- Richer environment change detection.
- Broader retention policies beyond exact duplicates.
- Better causal links between intervention, action, verification, and outcome.

---

## Beta 2.2 — Cognitive Runtime vertical slice — complete

### Delivered

- `memcoder_intervene` with `none`, `risk`, `brief`, and `plan` modes.
- Task archetype, belief separation, Transfer Delta, prediction/falsification,
  reuse check, and verification contract.
- Token-bounded cognition packets.
- Owner-scoped task checkpoints outside semantic guidance memory.
- Matching Python, CLI, and MCP runtime contracts.
- Local Codex Desktop plugin for automatic dogfooding.

### Exit work still required

- Run diverse real-project evaluations.
- Establish intervention usefulness and harmful-intervention baselines.
- Measure total token cost rather than packet size alone.
- Harden Codex plugin installation and lifecycle behavior.
- Demonstrate that automatic intervention produces a meaningful outcome delta.

---

# Critical path to exceptional developer cognition

The order below is deliberate. Each phase supplies the trusted input required
by the next.

```text
2.3 Utility Engine + Project Cortex
→ 2.4 Autopilot + Token Economy + Skill Intelligence
→ 2.5 Dreaming + Evaluation + Core Hardening
→ Beta 3 Productization
→ Release Candidate
→ Core 1.0
```

---

## Beta 2.3 — Utility Engine and Project Cortex — completed foundation

**Outcome:** MemCoder surfaces cognition because it changes the next developer
decision—not because two pieces of text look similar—and maintains enough
verified project state to continue correctly across sessions.

- **Estimated scope:** large
- **Depends on:** Beta 2.1 evidence substrate and Beta 2.2 intervention contract

Beta 2.3 ships only when both workstream gates pass.

> **Engineering status (0.2.3b1): implemented.** The provider-free runtime,
> public host surfaces, and focused regression checks are complete. The
> percentage-based gates below remain evaluation claims and require controlled
> held-out trials before they may be reported as achieved.

### Workstream A — Utility Engine

#### Developer experience

- Irrelevant memories disappear even when their confidence is high.
- Every surfaced item explains why it is useful now.
- The developer can mark guidance helpful, ignored, misleading, or harmful.
- MemCoder learns better abstention without weakening evidence requirements.

#### Engineering work

##### Task and decision framing

- Decompose the host request into task archetype, current decision, desired
  outcome, failure risk, environment, constraints, and proof need.
- Separate topic similarity from action similarity and verification similarity.
- Identify whether the host needs a warning, precedent, procedure, decision
  rationale, proof strategy, or no memory.

##### Utility-aware retrieval

- Add a decision-utility score alongside semantic relevance and confidence.
- Add a **utility veto** when a memory cannot change action, proof, or risk.
- Calibrate thresholds per task archetype and intervention mode.
- Use diversity selection so returned evidence is complementary rather than
  repetitive.
- Prioritize negative evidence when the cost of repeated failure is high.
- Penalize memories that were repeatedly ignored or misleading in comparable
  environments.

##### Intervention receipts

Every packet should expose:

```text
why now
what decision it can change
supporting evidence
applicability conditions
known differences
expected value
token cost
required verification
```

##### Utility feedback

- Record `helpful`, `ignored`, `misleading`, and `harmful` independently from
  the validity of the source memory.
- Link feedback to the exact retrieval, environment, action, and outcome.
- Prevent popularity from overriding provenance or contradictions.
- Support explicit mute and applicability correction without deleting history.

##### Retrieval debugger

- Explain why candidates ranked, failed a gate, or were withheld.
- Replay a query against alternative thresholds.
- Compare semantic rank with final utility rank.
- Export a compact diagnostic suitable for bug reports and research evaluation.

#### Standout research contribution

**Utility-gated memory:** a memory can be trusted yet correctly withheld because
it offers no decision value. This is a stronger standard than relevance-only
retrieval.

#### Utility Engine gate

- At least 90% precision at the first surfaced item.
- At least 90% correct abstention on no-memory tasks.
- Fewer than 5% irrelevant automatic interventions.
- Fewer than 1% harmful interventions in controlled trials.
- Utility feedback measurably improves later ranking on held-out tasks.

#### Explicitly postponed

- Dreaming.
- Cloud sync.
- Multi-agent sharing.
- Heavy GUI work beyond a minimal retrieval debugger.

---

### Workstream B — Project Cortex and durable situation awareness

This workstream ensures that a new session or different host can understand the
project's verified state without replaying raw chat history.

#### Developer experience

- Ask “where were we?” and receive a correct, bounded project brief.
- Recover decisions, constraints, unresolved risks, and next actions after a
  long gap.
- Know which facts are current, uncertain, stale, or contradicted.
- Hand work to another compatible agent without a giant continuation prompt.

#### Engineering work

##### Situation model

- Maintain verified project identity, environment, architecture constraints,
  important files, dependency state, active goals, and unresolved risks.
- Track facts, hypotheses, assumptions, questions, and deprecated beliefs as
  different state classes.
- Link state to evidence and expiration conditions.
- Update incrementally from host events instead of rescanning everything.

##### Decision memory

A decision record contains:

```text
decision
rationale
alternatives considered
why alternatives were rejected
supporting evidence
scope and owner
validity conditions
superseding event
verification or review
```

- Detect conflicting decisions.
- Surface the rationale when a later task would reverse a prior choice.
- Never treat an old decision as permanent when its conditions changed.

##### Environment and temporal validity

- Fingerprint relevant files, dependencies, configuration, branch, and optional
  revision information.
- Invalidate or penalize knowledge when its dependencies drift.
- Distinguish same-project evolution from unrelated-project transfer.
- Support explicit time-sensitive memory and review dates.

##### Project Resurrection

Compile a bounded brief containing:

- current objective;
- completed verified work;
- active decisions and constraints;
- unresolved failures and risks;
- working tree or environment caveats supplied by the host;
- relevant Skills and proof paths; and
- the next safe action.

##### Verified Handoff

- Export a signed or checksummed cognition capsule with selected state,
  evidence handles, Skills, and open work.
- Require receiving hosts to revalidate environment assumptions.
- Exclude secrets and raw transcripts by default.

#### Standout research contribution

**Evidence-bound situation continuity:** project state is reconstructed from
verified decisions and events rather than generated as an unsupported summary.

#### Project Cortex gate

- At least 90% correct state recovery on held-out session-resumption tasks.
- Bounded resurrection brief fits within a defined token ceiling.
- Stale decisions are withheld after relevant environment changes.
- Cross-host handoff preserves state without leaking excluded records.

---

## Beta 2.4 — Invisible Autopilot, Token Economy, and Skill Intelligence

> **Engineering status (0.2.4b1): implemented.** The lifecycle contract,
> fail-open attention governor, failure radar, verification planner, token
> ledger, reversible QA capture, versioned Skill contract, transfer compiler,
> composition checks, evolution candidates, and causal credit are implemented
> across Python, CLI, MCP, and the local Codex plugin. The quantitative release
> gates below still require the documented real-project evaluation runs.

**Outcome:** developers use ordinary prompts while MemCoder quietly prevents
known mistakes, returns more context than it consumes, and turns repeated
verified work into dependable procedural competence.

- **Estimated scope:** large
- **Depends on:** Utility Engine and Project Cortex

Beta 2.4 ships only when both workstream gates pass.

### Workstream A — Autopilot, Failure Radar, and token economy

#### Developer experience

- Install once; normal requests automatically receive cognition when useful.
- High-risk actions trigger a concise warning before execution.
- Familiar work becomes faster rather than more verbose.
- MemCoder failure never blocks the underlying host.
- One command pauses, inspects, or rolls back automatic learning.

#### Engineering work

##### Host lifecycle contract

One provider-neutral event model for:

```text
task_started
context_changed
before_plan
before_edit
before_tool
verification_started
verification_finished
task_completed
task_failed
```

- Mature Codex Desktop integration.
- Mature AGY integration.
- Reference SDK middleware for CLI, Python, and service automations.
- Capability negotiation so unsupported hosts degrade cleanly.

##### Attention governor

- Estimate expected benefit, failure cost, confidence, environment match, token
  cost, and interruption cost.
- Choose `none`, `risk`, `brief`, or `plan` at each lifecycle boundary.
- Avoid repeated intervention within one task unless state materially changes.
- Learn per-project and per-archetype intervention preferences.

##### Failure Radar

- Match planned actions against verified mistakes, rejected plans,
  contradictions, and verification failures.
- Trigger before destructive commands, migrations, dependency changes,
  releases, security-sensitive work, and repeated regressions.
- Return the failure mechanism, applicability check, and cheapest preventive
  verification—not a generic warning.

##### Verification planner

- Retrieve which test, build, assertion, render, review, or acceptance criterion
  previously caught the relevant failure.
- Scale proof depth to risk.
- Prefer existing project-native checks.
- Distinguish “command passed” from “requirement was actually verified.”

##### Minimum Sufficient Cognition

MemCoder's token-saving system should be distinct from generic summarization:

1. Return a one-line decision or warning first.
2. Reference evidence by stable handle.
3. Expand only the exact record requested by the host.
4. Reuse stable project facts without reinjecting their prose.
5. Deduplicate overlapping memories and instructions.
6. Stop retrieval when additional context cannot change the action.

##### Token ledger

Measure:

- retrieval and reranking cost;
- tokens injected into the host;
- evidence expansions;
- investigation and tool calls avoided;
- repeated context avoided through handles;
- final net token dividend; and
- correctness or rework trade-offs.

##### Automatic verified capture

- Convert passing CI, tests, builds, reviews, and host assertions into candidate
  evidence automatically.
- Require the same QA admission as manual records.
- Group one task's events into an atomic, reversible learning batch.
- Never infer success solely because the host stopped working.

#### Standout research contributions

- **Failure Radar:** prospective memory that prevents recurrence before action.
- **Minimum Sufficient Cognition:** optimize for decision value per token, not
  compression ratio alone.

#### Autopilot and token-economy gate

- Supported host setup completes in under two minutes.
- Ordinary prompts invoke correct lifecycle behavior.
- At least 15% median net token reduction or 20% less repeated investigation
  and rework, with no correctness regression.
- Known failure families are intercepted before action in at least 80% of
  eligible replay cases.
- Fault injection proves fail-open host behavior and reversible learning.

---

### Workstream B — Skill Intelligence and adaptive planning

This workstream turns repeated verified work into dependable procedural
competence rather than merely retrieved advice.

#### Developer experience

- Proven workflows execute as concise, inspectable plans.
- Skills adapt when the project differs without pretending the differences do
  not exist.
- Repeated failures lower Skill trust automatically.
- Compatible Skills can compose; conflicting Skills refuse composition.

#### Engineering work

##### Skill contract

Every Skill becomes a versioned program-like object:

```text
purpose
preconditions
inputs
ordered steps
decision points
expected observations
verification
failure handling
rollback
applicability limits
supporting evidence
version history
health
```

##### Skill compiler

- Promote patterns only from QA-approved support.
- Extract stable procedure from incidental implementation detail.
- Preserve negative cases and rejected variants.
- Produce a deterministic provider-free baseline compiler.
- Allow optional model providers to propose richer candidates, never bypass QA.

##### Safe Transfer Compiler

For the current task, compile:

- matched preconditions;
- missing or changed conditions;
- invalid assumptions;
- directly reusable steps;
- steps requiring adaptation;
- known failure boundaries; and
- current verification and rollback.

This replaces “retrieve similar solution” with an explicit transfer program.

##### Skill evolution

- Propose new versions when later evidence improves, narrows, or contradicts a
  procedure.
- Preserve old versions and their outcome history.
- Use project-specific overlays instead of cloning whole Skills.
- Detect plan-execution drift and attribute outcomes to the steps actually used.

##### Skill composition

- Compose Skills only when preconditions, state mutations, proof, and rollback
  are compatible.
- Detect ordering conflicts and shared-resource risks.
- Keep composed plans bounded; no open-ended autonomous objective expansion.

##### Causal credit

- Separate “Skill was present” from “Skill caused the successful decision.”
- Track which step or warning changed host behavior.
- Avoid raising Skill confidence when the host ignored it or solved by another
  route.

#### Standout research contribution

**Evidence-compiled procedural memory:** Skills behave like versioned,
test-carrying programs with preconditions and rollback rather than prompt text.

#### Skill Intelligence gate

- Skill-guided runs outperform isolated Experience retrieval on held-out task
  families.
- Composition refuses known conflicts and passes combined verification.
- Skill confidence tracks verified outcomes rather than invocation count.
- A failed or drifted plan cannot silently reinforce the original Skill.

---

## Beta 2.5 — Dreaming, Evaluation, and Core Hardening

**Outcome:** MemCoder improves between tasks through testable candidate learning,
then proves and hardens the complete local cognitive loop across real developer
work.

- **Estimated scope:** large and research-heavy
- **Depends on:** utility feedback, causal outcomes, versioned Skills, and strong QA

Beta 2.5 ships only when both workstream gates pass.

### Workstream A — Dreaming, Failure Frontiers, and cognitive simulation

#### Developer experience

- Idle-time consolidation proposes useful patterns and missing tests.
- Repeated failures produce explicit boundary cases.
- Candidate insights arrive with evidence, counterexamples, and uncertainty.
- Developers can preview, approve, reject, or postpone every promotion.

#### Dream cycle

```text
select evidence
→ replay related episodes
→ identify stable pattern or unresolved contradiction
→ generate candidate Principle, Skill revision, or hypothesis
→ search counterexamples and environment conflicts
→ simulate against held-out memories or tasks
→ calibrate confidence
→ preview for approval or reject
```

#### Engineering work

##### Cognitive replay

- Group Experiences by decision, causal mechanism, failure family, environment,
  and verification—not only topic.
- Find recurring assumptions, duplicated investigation, and missed warnings.
- Contrast successful and failed episodes.

##### Failure Frontier

- Generalize verified mistakes into candidate boundary conditions.
- Generate the smallest test likely to expose each boundary.
- Track which boundaries remain hypothetical versus reproduced.
- Feed confirmed boundaries back into Failure Radar and Skill verification.

##### Counterfactual memory

- Preserve serious alternatives that were tried or rejected and why.
- Ask what evidence would have made the alternative correct.
- Use counterfactuals to constrain generalization and Skill transfer.

##### Memory sandbox

- Evaluate candidate Principles and Skills against held-out prior episodes.
- Measure whether a candidate improves decisions, adds noise, or causes negative
  transfer before promotion.
- Quarantine candidates that require more evidence.

##### Self-calibration

- Compare predicted benefit and confidence with actual verified outcomes.
- Adjust intervention and promotion thresholds from evidence.
- Detect systematic overconfidence by task archetype or environment.

##### Optional semantic reasoners

- Provider adapters may assist clustering, analogy, critique, hypothesis
  generation, and counterexample search.
- Provider-generated output remains candidate data.
- The provider-free Core can still run deterministic consolidation and review.
- No provider receives private memory without explicit user policy.

#### Non-negotiable Dreaming rules

- Dreaming creates candidates, never facts.
- No silent promotion, deletion, or overwrite of trusted knowledge.
- Every candidate exposes source evidence and counterexample search.
- Dream runs have explicit time, cost, token, and privacy budgets.
- All changes are versioned and reversible.

#### Standout research contribution

**Evidence-gated adversarial Dreaming:** offline consolidation must survive
counterexample search and a memory sandbox before it can influence trusted
behavior.

#### Dreaming research gate

Compare:

1. episodic memory only;
2. utility-gated retrieval;
3. Skills and Transfer Compiler;
4. Dreaming without adversarial checks; and
5. evidence-gated adversarial Dreaming.

Measure precision, negative transfer, hidden-check correctness, rework, token
use, Skill quality, pollution, and calibration.

---

### Workstream B — Evaluation, host ecosystem, and Core hardening

This workstream proves that the cognitive architecture works across real
developer tasks and supported hosts before expansion into cloud and teams.

#### Evaluation program

##### Task families

- debugging and regression repair;
- validation and failure handling;
- dependency and configuration changes;
- migrations and data transformations;
- security-sensitive changes;
- rendering and visual QA;
- documentation and architecture drift;
- release engineering;
- project resumption and agent handoff; and
- repeated domain workflows.

##### Experimental conditions

- host baseline without MemCoder;
- persistent Experience only;
- utility-gated retrieval;
- Project Cortex;
- Autopilot and Failure Radar;
- Skill-guided planning;
- Dreaming candidates; and
- optional provider-assisted intelligence.

##### Metrics

- pass rate and hidden-check correctness;
- retrieval precision and abstention;
- harmful and ignored intervention rates;
- token use and context expansion;
- time, tool calls, and rework;
- repeated-failure prevention;
- project-resurrection accuracy;
- calibration and negative transfer;
- memory pollution and stale-memory rate; and
- user trust and override frequency.

#### Host ecosystem

- Stable Codex Desktop plugin.
- Stable AGY integration.
- Reference MCP configuration.
- Python middleware and CLI automation kit.
- Host certification tests for lifecycle, fallback, evidence, and privacy.
- Clear support matrix rather than claiming universal compatibility.

#### Core hardening

- Cross-platform installation and upgrade tests.
- Migration fixtures spanning every public schema.
- Crash recovery and atomic learning batches.
- Backup, restore, rollback, and corruption drills.
- Threat model for imported instructions, shared memories, plugins, and cloud.
- Performance budgets for startup, retrieval, storage, and background work.
- Opt-in diagnostics with no memory contents by default.

#### Evaluation and hardening gate

- Meet the 9/10 developer bar on a representative evaluation set.
- Publish reproducible methodology and limitations.
- Supported integrations require no elaborate per-task prompts.
- No unresolved data-loss, migration, privacy, or fail-open blocker remains.

---

# Beta 3 — Productization and collective cognition

Beta 3 turns the proven local cognitive engine into a controllable product. It
does not relax the evidence model. The capabilities below are workstreams inside
one productization phase, not four mandatory standalone releases. Memory Studio
and personal continuity come first; team and multi-agent cognition remain the
last workstream.

## Workstream A — Memory Studio and developer control

**Outcome:** cognition becomes visible, understandable, and correctable without
editing database files or writing CLI JSON.

### Product surface

- Home view: project state, recent interventions, open risks, and cognition
  health.
- Memory explorer: Experience, Reflection, Mistake, Principle, Skill, and plan.
- Provenance graph and evidence viewer.
- Retrieval debugger with ranking and gate explanations.
- Decision timeline and Project Resurrection preview.
- Skill editor, version diff, health, and outcome history.
- Dream inbox for candidate approval and rejection.
- Contradiction resolution and stale-memory review.
- Token dividend, intervention value, and failure-prevention metrics.
- Backup, restore, export, import, retention, and rollback controls.

### UX principles

- Default view answers “what does MemCoder believe, and why?”
- Every automatic behavior can be paused or overridden.
- No graph visualization merely for spectacle; every view must support a user
  decision.
- Advanced provenance remains available without overwhelming first-time users.

### Release gate

- A developer can diagnose and correct a bad intervention without the CLI.
- All destructive operations require preview and remain recoverable.
- Studio works entirely against local Core.

---

## Workstream B — Personal cloud continuity

**Outcome:** one developer's cognition follows them across devices while local
Core remains authoritative and usable offline.

### Core work

- End-to-end encrypted sync for selected projects and memory classes.
- Device identity, revocation, and recovery.
- Conflict-safe record and provenance synchronization.
- Local semantic indexing where practical.
- Selective sync, retention, and data residency controls.
- Cloud backup and restore independent from hosted inference.
- Explicit separation between sync metadata and memory content.

### Non-negotiable rule

Cloud availability must never be required to use MemCoder Core. Sync failure
must not corrupt or block local cognition.

### Release gate

- Multi-device convergence passes conflict and offline-recovery tests.
- Encryption and key-management design receive external review.
- Users can export and delete all hosted data.

---

## Workstream C — Optional MemCoder Intelligence

**Outcome:** users who choose a model provider receive richer cognition without
changing Core's trust boundary.

### Capabilities

- Better semantic extraction from complex outcomes.
- Cross-domain analogy proposals.
- Contradiction and counterexample critique.
- Richer Skill synthesis and plan review.
- Deeper Dreaming and hypothesis generation.
- Natural-language exploration in Memory Studio.

### Provider architecture

- User-selectable providers and models.
- Explicit capability and privacy contracts.
- Per-operation routing rather than one model controlling everything.
- Cost, token, latency, and data-sharing budgets.
- Provider output marked as candidate until Core verification admits it.
- Provider-free fallback for every safety-critical operation.

### Product boundary

This may support a paid Intelligence edition, but pricing must follow measured
value. A stronger model does not justify a premium unless it improves retrieval,
planning, consolidation, or developer outcomes in controlled evaluation.

---

## Workstream D — Teams and multi-agent cognition

**Outcome:** verified organizational learning can be shared safely after
personal cognition, provenance, and permissions are mature.

### Team cognition

- Organization, project, team, and personal namespaces.
- Roles, permissions, approval workflows, and audit trails.
- Shared Skills and verification playbooks with complete provenance.
- Project-specific overlays and controlled cross-project transfer.
- Contradiction resolution across contributors.
- Secret and sensitive-context exclusion policies.
- Knowledge ownership, attribution, deprecation, and review schedules.

### Multi-agent coordination

- Shared plans with explicit ownership of steps and proof.
- Agent capability declarations and task assignment constraints.
- Common situation model with isolated private working memory.
- Conflict detection when agents act on incompatible assumptions.
- Verification aggregation without treating consensus as evidence.
- Handoff and recovery when one agent fails or disappears.

### Why this remains late

Multi-agent cognition magnifies every earlier weakness. Poor retrieval becomes
shared misinformation; weak provenance becomes organizational confusion; bad
automation becomes coordinated error. It follows—not precedes—strong personal
cognition and control.

### Release gate

- Permission and isolation tests prevent unauthorized retrieval.
- Shared knowledge retains contributor, evidence, and validity history.
- Multi-agent runs improve throughput without reducing correctness or auditability.

---

# Release Candidate — Stability and promise freeze

The Release Candidate is not a feature phase. It freezes the Core promise and
removes reasons not to trust it.

## Required work

- Stable CLI, Python, MCP, storage, plugin, and lifecycle contracts.
- Documented compatibility and deprecation policy.
- Migration, backup, restore, export, rollback, and disaster-recovery testing.
- Security review of local storage, imports, plugins, sync, and provider access.
- Performance and token budgets enforced in CI.
- Accessibility and usability review for Memory Studio.
- Complete installation, troubleshooting, privacy, and architecture docs.
- Reproducible evaluation report with limitations and failed experiments.
- Clean separation of Core, Intelligence, Cloud, and Teams capabilities.

## RC blocker policy

Any unresolved data-loss risk, silent learning path, privacy leak, unsupported
automatic action, unexplained intervention, or correctness regression blocks
1.0 regardless of feature completeness.

---

# MemCoder Core 1.0 — Dependable local cognition

## Defensible product claim

> MemCoder is a dependable, local-first cognition layer that helps compatible
> AI agents retain verified project knowledge, recover state, transfer prior
> learning safely, reuse proven procedures, prevent repeated failures, verify
> outcomes, and improve over time with less repeated context.

## What Core 1.0 includes

- Durable evidence and provenance substrate.
- Utility-gated retrieval and correct abstention.
- Project Cortex and verified handoff.
- Cognitive Autopilot on supported hosts.
- Failure Radar and verification planning.
- Minimum Sufficient Cognition and token ledger.
- Versioned Skills, safe transfer, and adaptive planning.
- Evidence-gated Dreaming candidates.
- Local Memory Studio and full user control.
- Stable backup, migration, export, rollback, and privacy controls.
- Published real-project evaluation.

## What Core 1.0 does not require

- A hosted model API.
- Ollama, CUDA, or a local generation server.
- Cloud storage.
- Team or multi-agent features.
- Raw conversation retention.
- Blind autonomous modification.

---

# Product editions after Core proves value

Exact pricing is deliberately deferred until the evaluation program measures
real developer value.

| Edition | Product promise |
| --- | --- |
| **MemCoder Core** | Local, provider-free verified cognition for individuals and open integrations. |
| **MemCoder Intelligence** | Optional provider-powered semantic synthesis, critique, advanced Dreaming, and richer planning. |
| **MemCoder Cloud** | Encrypted personal continuity, backup, and device synchronization. |
| **MemCoder Teams** | Shared verified Skills, governance, permissions, audit, and multi-agent coordination. |

Paid editions must fund convenience or demonstrated intelligence gains. They
must not weaken the usefulness, portability, or safety of local Core.

---

# Research program and paper strategy

MemCoder can support a meaningful research contribution if experiments isolate
mechanisms rather than reporting one successful demo.

## Candidate research claims

1. **Proof-carrying memory reduces negative transfer.**
2. **Utility-gated intervention outperforms similarity-only retrieval.**
3. **Verification-first retrieval improves robustness on unseen task variants.**
4. **Minimum Sufficient Cognition produces a net token dividend without lower
   correctness.**
5. **Failure Radar prevents recurrence more effectively than post-task memory.**
6. **Evidence-compiled Skills transfer better than episodic examples alone.**
7. **Adversarial Dreaming improves generalization with less memory pollution
   than unconstrained consolidation.**
8. **Evidence-bound project state improves cross-session and cross-host
   continuity over transcript summarization.**

## Required ablations

- no memory;
- similarity-only Experience retrieval;
- confidence and validity gates;
- utility veto and abstention;
- proof-carrying retrieval;
- Project Cortex;
- Failure Radar;
- Skills without Transfer Compiler;
- Skills with Transfer Compiler;
- unconstrained Dreaming;
- adversarial evidence-gated Dreaming; and
- provider-free versus optional-provider intelligence.

## Evaluation integrity

- Predefine primary metrics and failure criteria.
- Use hidden checks and real repository tasks.
- Report negative transfer and ignored interventions.
- Count MemCoder's own tokens, latency, and tool calls.
- Separate statistical improvement from memorable anecdotes.
- Publish tasks and harnesses where licensing and privacy permit.
- Report where MemCoder makes outcomes worse.

---

# Long-range research horizons

These are intentionally post-1.0 research directions, not commitments for the
current critical path.

## Causal developer memory

Move beyond “this task resembled that task” toward evidence about which action,
warning, Skill step, or verification actually caused an outcome.

## Cognitive branching

Allow agents to explore alternative plans in isolated cognition branches,
compare verified results, and merge only supported learning.

## Private cross-project pattern learning

Learn reusable failure and verification patterns across projects without
exposing project content, potentially through local abstraction or privacy-
preserving aggregation.

## Federated Skill intelligence

Share validated procedural patterns between consenting users or teams while
preserving provenance, ownership, environment constraints, and revocation.

## Long-lived agent identity

Study how one agent or team can accumulate stable, inspectable competence over
months without turning memory into an unreviewable personality profile.

## Cognitive simulation

Use accumulated evidence to simulate likely plan failures before implementation,
with explicit uncertainty and no claim that simulation is proof.

---

# Sequencing and priority rules

When priorities conflict, use this order:

1. Data integrity and reversibility.
2. Retrieval precision and correct abstention.
3. Verification and negative-transfer prevention.
4. Measurable developer effort and token savings.
5. Automatic host integration.
6. Situation continuity and procedural intelligence.
7. Dreaming and optional model intelligence.
8. GUI, cloud, teams, and multi-agent expansion.

## What should not happen in parallel

- Do not build full Dreaming before utility feedback and counterexamples exist.
- Do not build cloud sync before local migrations and rollback are dependable.
- Do not expand multi-agent behavior before permissions and provenance are
  externally testable.
- Do not add provider intelligence before Core can measure whether it helped.
- Do not optimize token count by removing verification or trust context.
- Do not call a feature automatic if users still need a special prompt.

## Immediate next milestone

The current implementation line is **Beta 2.4: Invisible Autopilot, Token
Economy, and Skill Intelligence**. Its engineering foundation is implemented;
the quantitative release gates remain an evaluation requirement.

The first deliverable should be a closed-loop intervention record:

```text
task and decision frame
→ candidate memories
→ gates and utility score
→ selected intervention or abstention
→ host action
→ verification result
→ helpful / ignored / misleading / harmful outcome
→ later ranking update
```

Until that loop works, additional intelligence is mostly unmeasured potential.

---

# Explicit non-goals

- No claim of consciousness or human-equivalent cognition.
- No unrestricted autonomous self-modification.
- No durable learning without evidence.
- No hidden model, provider, or cloud dependency in Core.
- No blind reuse of stale or merely similar memories.
- No raw transcript collection as the default memory strategy.
- No silent promotion of Dream candidates.
- No shared cognition without ownership and permissions.
- No feature-count definition of intelligence.
