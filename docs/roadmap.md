# MemCoder roadmap

> **MemCoder is a provider-independent cognitive control layer for AI agents.**
> It does not merely retrieve memories. It decides what an agent should attend
> to, reuse, verify, avoid, and learn from verified work.

```text
Verified Experience
   ├─ Reflection: reasoning observation
   ├─ Mistake / risk: negative evidence
   └─ Principle: validated generalization
          └─ Skill: reusable procedure
                 └─ Plan: current-task application
```

## Product principles

- **Local-first and provider-independent:** Core remains useful without a model
  API, Ollama, CUDA, or a cloud account.
- **Evidence before learning:** no automatic durable memory write without
  verification evidence.
- **Guidance, not authority:** retrieved knowledge is a hypothesis; the host
  must inspect the current project and verify the outcome.
- **Smallest useful intervention:** do not inject memory, consume tokens, or
  write code unless it is likely to help.
- **Provenance over opaque intelligence:** every Principle, Skill, plan, and
  Dream candidate must explain its supporting evidence.

---

## Alpha — Cognition foundation ✅

**Goal:** prove persistent semantic memory and a provider-independent direction.

### Established

- Persistent semantic storage.
- Experience, Reflection, Principle, and Mistake concepts.
- Owner-scoped memory and early hierarchical retrieval.
- Initial reflection and autonomous-learning experiments.
- Early Ollama/Qwen experiments.

### Limitation

Learning quality, retrieval safety, and installation were not yet strong enough
for dependable agent workflows. Parts of the early path depended on a local
model provider.

---

## Beta 1 — Provider-free verified memory ✅

**Goal:** make memory-assisted agent work safe, usable, and defensible.

### Delivered

- Provider-free MCP and CLI workflow.
- Query-relevant, confidence-gated retrieval.
- Project/owner isolation and controlled shared retrieval.
- Memory quality admission and reflection validation.
- Markdown instruction import with preview/approval.
- AGY proof that stored memory can help a similar unseen task.
- Optional legacy Ollama path; not required for Core.

### What it proved

```text
Agent task
→ retrieve trusted local memory
→ host solves and verifies
→ store validated outcome
→ future related tasks receive guidance
```

---

## Beta 1.1 — Adoption and onboarding ✅

**Goal:** make Beta 1 easy for other people to install and try.

### Delivered

- PyPI installation.
- `memcoder setup-agy` onboarding.
- Markdown import by file path.
- Installation documentation, reusable prompts, and package hardening.

---

## Beta 2.0 — Verified Skills and bounded plans ✅

**Release:** `0.2.0b1`

**Goal:** turn validated memory into reusable behavior without making Core
provider-dependent.

### Delivered

- QA evidence gate for outcome admission.
- Compact token-bounded cognition briefs.
- Evidence-backed Skill promotion.
- Bounded, transparent Skill-guided plans.
- Plan outcome audits and derived Skill health.
- Reflection provenance to approved source Experiences.
- Baseline / memory-guided / skill-planned evaluation reporting.
- Controlled transfer evidence: valid MemCoder-assisted runs passed private
  robustness checks where matched no-memory baselines failed.

### Current limitation

The user or host still has to deliberately invoke MemCoder. Retrieval is safer
than Alpha, but it is not yet a full cognitive control runtime.

---

# The Cognitive Runtime roadmap

## Long-term cognitive architecture

MemCoder becomes the best cognition layer by developing four connected
capabilities—not by becoming a generic chatbot or an opaque autonomous agent.

```text
1. Cognitive Runtime
   → attention, transfer, working memory, planning, verification, automation

2. Memory Intelligence
   → provenance, validity, contradiction, environment awareness, skill growth

3. Dreaming
   → offline consolidation, hypotheses, counterexamples, self-calibration

4. Collective Cognition
   → inspection, cloud continuity, safe sharing, multi-agent coordination
```

Each layer remains evidence-bound and useful without a mandatory model provider.

## Beta 2.1 — Memory Intelligence, durable substrate, and evidence graph

**Primary goal:** evolve the Alpha-era store into a durable cognition substrate
before building Dreaming, cloud sync, or serious multi-agent behavior.

### Implementation status — complete

The first storage-foundation slice is complete locally:

- New guidance records receive a stable `record_id`, schema version, lifecycle
  state, timestamps, and revision number; a content fingerprint is now only a
  duplicate-detection compatibility field.
- Mutations update a record in place, preserving IDs already referenced by
  Reflections, Skills, and future provenance edges.
- Plan execution audits now live in a separate append-only local audit log
  rather than consuming semantic guidance-index capacity.
- Skill health reads those audits directly, preserving QA feedback without
  making audits retrievable as guidance.
- A durable, typed provenance graph records `derived_from`, `supports`, and
  `validated_by` links for new verified outcomes, Reflections, Principles, and
  Skills; legacy metadata can be backfilled through the storage migration.
- Lifecycle state and optional host environment fingerprints now affect
  retrieval: only trusted records are used automatically, incompatible projects
  are withheld, and same-project fingerprint drift is surfaced as a penalty.
- Retrieved memories now carry a proof contract: direct provenance evidence,
  environment conditions, transfer risks, and required current-project
  verification; the compact brief retains only a budget-safe proof status.
- Local operations now include read-only storage status, portable JSON export,
  timestamped ZIP backup, and conservative merge restore followed by a
  rebuild of the semantic index. Restore never deletes local cognition.
- Controlled retention now previews only exact duplicate records; explicit
  apply marks a duplicate `superseded` and records a `supersedes` provenance
  edge. Destructive consolidate-and-replace behavior is retired.
- Contradictions are explicit and evidence-preserving: reporting one links both
  records, marks both `contradicted`, and withholds them from automatic reuse;
  resolution restores a reviewed winner and supersedes the alternative.
- QA now retains a compact verification playbook. Retrieval exposes it through
  the proof contract and gives concrete proof paths a small ranking advantage.
- Default durable storage now lives in a per-user data directory. The migration
  command imports legacy workspace Chroma, SQLite, provenance, and audit data.

Future refinements can broaden environment policies and retention heuristics,
but the durable, evidence-bound substrate required before Autopilot is now in
place.

### Core work

- Immutable record IDs, revisions, schema versions, migrations, backup, export,
  and restore.
- A local source of truth separate from the rebuildable vector index.
- Separate retrieval-eligible knowledge from non-guidance audit/log records.
- Stable provenance edges: `derived_from`, `supports`, `supersedes`,
  `contradicts`, `validated_by`, and `applies_to`.
- Environment fingerprints: repository/project identity, relevant files,
  dependency/configuration context, and optional revision information.
- Memory validity states: `candidate`, `trusted`, `superseded`,
  `contradicted`, and `deprecated`.
- **Proof-carrying memory:** retrieved guidance includes supporting evidence,
  applicability conditions, risks, and the required verification method.
- **Verification-first retrieval:** retrieve the best way to prove a transfer
  before prioritizing a past implementation recipe.
- **Verification memory:** learn which checks, tests, builds, renders, and
  acceptance criteria actually caught the important failure.
- Hybrid, field-aware retrieval and contradiction-aware ranking.
- Default local storage in a user-data location rather than package files.
- Memory pressure controls: retention, compression, consolidation previews, and
  safe archival of stale or superseded knowledge.

### Release gate

- Existing databases migrate without broken Reflection or Skill links.
- Audit records no longer consume guidance-index capacity.
- A stored solution can be marked stale rather than followed blindly after its
  relevant environment changes.

---

## Beta 2.2 — Cognitive Runtime and Autopilot

**Primary goal:** make MemCoder an invisible, token-aware catalyst in compatible
agent workflows, once its memory substrate is safe enough to automate.

### Implementation status — first vertical slice complete

- `memcoder_intervene` now compiles a bounded Cognitive Packet and selects
  `none`, `risk`, `brief`, or `plan` without a model provider.
- Packets include task archetype, belief separation, Transfer Delta, a
  prediction/falsification contract, a pre-edit reuse check, and required proof.
- Owner-scoped task checkpoints persist bounded working state outside semantic
  guidance memory.
- The Python API, CLI, and MCP expose the same runtime contract.
- A validated Codex desktop plugin bundles the MCP server and an implicitly
  invoked cognition workflow Skill for local dogfooding.

The phase is not release-complete until diverse real-project evaluations show
measurable benefit without correctness or token regressions.

```text
Task begins
→ should MemCoder intervene?
→ retrieve only useful evidence
→ compute the safe transfer to this task
→ host acts and verifies
→ QA-gated learning updates future behavior
```

### Core work

- **Host-native Autopilot:** mature AGY integration and SDK wrappers that invoke
  the same cognition runtime at task, verification, and outcome boundaries.
- **Attention / intervention policy:** decide whether to retrieve nothing, one
  risk card, a compact brief, or a Skill-backed plan.
- **Cognitive Budgeter:** rank candidate guidance by expected value per token:
  relevance, evidence quality, environment compatibility, risk reduction,
  reuse value, staleness, contradiction risk, and token cost.
- **Transfer Delta:** compare a past successful solution with the current task
  and return explicit matches, differences, assumptions, risks, safe reuse, and
  required proof.
- **No-op / reuse detector:** before edits, ask whether the requirement already
  exists in the project, standard library, native platform, or an installed
  dependency; prefer the smallest safe action.
- **Working memory state:** compile known facts, constraints, risks, open
  questions, suggested action, verification requirements, and active task
  archetype into one compact task state.
- **Belief firewall:** distinguish verified facts, working hypotheses,
  untrusted candidates, and deprecated knowledge.
- **Task archetypes:** give validation, integration, rendering, transformation,
  dependency, security, and documentation tasks different retrieval and
  verification policies.
- **Codex plugin:** the local dogfooding bundle is complete. Published
  marketplace distribution and deeper host-native lifecycle hooks remain gated
  on real-project evaluation of the cognitive runtime.

### Release gate

- A user can install an adapter and use a normal host workflow without long
  per-task prompts.
- Automatic retrieval improves pass rate, rework, token use, or tool use on
  matched tasks without lowering correctness.
- Automatic recording still requires approved evidence.

---

## Beta 2.3 — Autonomous learning, Failure Frontier, and Dreaming

**Primary goal:** improve memory between tasks without inventing trusted facts.

```text
Approved Experiences
→ cluster patterns and detect gaps
→ candidate principle / skill / hypothesis
→ generate counterexamples and contradictions
→ validate, review, or reject
→ only then update trusted knowledge
```

### Core work

- **Dream runs:** local scheduled or idle-time consolidation with explicit time
  and token budgets.
- **Evidence-gated adversarial Dreaming:** generated Principles or hypotheses
  must survive counterexample, contradiction, and provenance checks before
  becoming trusted.
- **Failure Frontier:** derive likely boundary cases and verification tests from
  past failures, mistakes, and rejected plans.
- **Knowledge-gap queue:** identify repeated tasks with no useful memory and
  prioritize learning after they are successfully verified.
- **Cognitive replay:** inspect sequences of related Experiences to identify
  recurring assumptions, outcomes, and missed opportunities.
- **Plan–execution drift detection:** flag when a host’s actual changes depart
  materially from the evidence-backed plan.
- Candidate Principle/Skill review workflow and provenance graph inspection.
- **Skill evolution:** propose a new Skill version when later evidence improves,
  narrows, or contradicts a previous procedure; preserve the old version and
  its history rather than overwriting it.
- **Composed cognition:** combine compatible Skills only when their assumptions,
  evidence, and verification rules do not conflict.
- **Self-calibration:** compare expected retrieval/plan confidence with verified
  outcomes so confidence thresholds improve from evidence rather than intuition.

### Non-negotiable rule

Dreaming may create candidates. It must never silently rewrite, delete, or
promote trusted knowledge without evidence or explicit approval.

### Research gate

Compare episodic memory alone, Skills/plans, and evidence-gated Dreaming on
retrieval precision, hidden-check correctness, rework, token use, pollution,
and transfer quality.

---

## Beta 2.4 — Cognitive evaluation, intelligence expansion, and host ecosystem maturity

**Primary goal:** demonstrate that the Cognitive Core works across real hosts
and real task families, not just a narrow controlled benchmark.

### Core work

- Mature Codex plugin, AGY adapter, and reference SDK integration.
- Mode controls: `off`, `assist`, `automatic`, and `strict`.
- Per-project cognition policies, privacy controls, and token budgets.
- Reproducible benchmark suite with baseline, memory-guided, and Autopilot
conditions.
- Measurements for retrieval precision, belief calibration, token use, tool
calls, rework, no-op detection, verification quality, and negative transfer.
- Real-project evaluations across multiple task archetypes:
  validation, data transformation, integration, failure handling, rendering,
  dependency changes, and documentation drift.
- Portable project cognition packs: approved project rules, trusted Skills,
  verification playbooks, and selected Experiences.
- Optional-provider interface design, without making any provider a Core
  dependency. This prepares a future user-selected intelligence layer for
  semantic extraction, analogy, critique, and advanced plan review.
- Research-grade ablations for retrieval, Transfer Delta, no-op detection,
  Skills, Dreaming, and optional intelligence.

### Release gate

- MemCoder can show a repeatable benefit on diverse real-project tasks.
- The host ecosystem is simple enough that users do not need elaborate prompts
  to receive cognitive support.

---

## Beta 3 — Memory Studio, cloud continuity, and team cognition

**Goal:** make cognition inspectable, controllable, and portable across a
person’s devices.

### Memory Studio

- Browse memories, evidence, provenance, retrieval traces, Skills, plans,
  Dream candidates, and Skill health.
- Approve, reject, deprecate, merge, or restore knowledge.
- Inspect Transfer Deltas, belief states, and Failure Frontiers.

### Personal cloud continuity

- Encrypted cross-device synchronization.
- Local-first source of truth and local semantic indexing where practical.
- Backup, restore, device management, and explicit data-retention controls.

Cloud sync must not become a hidden requirement for MemCoder Core.

### Team cognition and multi-agent coordination

- Shared namespaces, ownership, roles, permissions, and approval workflows.
- Shared Skills and verification playbooks with complete provenance.
- Safe cross-project transfer boundaries.
- Contradiction/conflict resolution and team audit trails.
- Multi-agent coordination around shared plans, risks, and verification.

Beta 3 may ship these in staged previews, but they belong to one connected
product capability: inspectable personal cognition that can later become safe
collective cognition.

## Core 1.0 — Dependable local cognition layer

**Goal:** make a clear, defensible promise about MemCoder Core.

### Required before 1.0

- Stable CLI, MCP, Python API, adapter, and plugin contracts.
- Safe migrations, backups, restore, export, and rollback.
- Strong cross-platform installation and update experience.
- Cognitive Autopilot on supported hosts.
- Broad reproducible evaluation on real projects.
- Demonstrated retrieval precision, memory quality, transfer value, and token /
  rework benefit.
- Complete privacy, storage, provider, and retention documentation.
- Memory Studio inspection and user control.

### What 1.0 can claim

> MemCoder is a dependable, local-first cognition layer that helps compatible
> AI agents retain verified knowledge, compute safe transfer from prior work,
> reuse proven procedures, verify outcomes, and improve over time.

---

## Optional products after the Cognitive Core is mature

### MemCoder Intelligence

Optional user-chosen provider assistance for richer extraction, semantic
consolidation, analogy, contradiction critique, and advanced plan review.

It must strengthen Core—not become a hidden dependency.

### MemCoder Cloud and Teams

Hosted sync, organization controls, shared cognition, and collaboration built
on the stable local record/provenance model.

---

## Explicit non-goals

- No claim of consciousness or unrestricted autonomous self-modification.
- No durable learning without evidence.
- No hidden provider or cloud dependency in Core.
- No blind reuse of stale memories.
- No cloud/team rollout before ownership, provenance, and privacy are ready.
