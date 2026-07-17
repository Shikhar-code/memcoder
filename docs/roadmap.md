# MemCoder roadmap

```text
Experience → Reflection → Principle → Skill → Plan
```

## Alpha — Cognition foundation

**Goal:** prove the core memory hierarchy and provider-independent architecture.

### What Alpha established

- Persistent semantic memory storage.
- Experience, Reflection, Principle, and Mistake memory types.
- Owner-scoped memory.
- Hierarchical retrieval.
- Early reflection and autonomous-learning experiments.
- Initial Ollama/Qwen-based experimentation.

### What it could do

- Store and retrieve memories across sessions.
- Generate early learning artifacts.
- Demonstrate the cognition hierarchy concept.

Alpha limitation: learning and retrieval were not yet trustworthy enough for
real agent workflows, and parts depended on a local model provider.

## Beta-1 — Provider-free agent cognition

**Goal:** make MemCoder safe, usable, and defensible with AGY.

### What Beta-1 accomplished

- Provider-free MCP workflow through `memcoder_prepare` and `memcoder_record`.
- Persistent Experiences, Reflections, Principles, and Mistakes.
- Query-relevant, confidence-gated retrieval.
- Owner isolation and optional shared-memory retrieval.
- Memory-quality admission checks.
- Reflection validation: reflections describe reasoning, not disguised solutions.
- Rejection feedback when memory quality is poor.
- Source provenance for imported instructions.
- Optional Ollama/Qwen legacy path; it is not required for normal use.
- AGY proof: related prior memory was retrieved, AGY used it on a similar but
  different task, and memory-guided work passed a holdout regression that a
  no-memory control failed.
- PyPI package publishing and `memcoder setup-agy` onboarding.

### What Beta-1 can do

```text
AGY task
→ retrieve trusted local memory
→ AGY solves and verifies
→ MemCoder stores a validated outcome
→ related future tasks receive relevant guidance
```

- Bootstrap project rules from approved Markdown files.
- Reject descriptive README prose rather than polluting memory.
- Preserve memory source metadata.
- Work without Ollama, Qwen, CUDA, or a local generation server.

Beta-1 is reliable memory-assisted coding, not autonomous planning or team
cognition yet.

## Beta-1.1 — Adoption and onboarding

**Goal:** make Beta-1 practical for other people to install and use.

### What it adds

- PyPI installation: `pip install memcoder`.
- AGY setup command: `memcoder setup-agy`.
- Markdown instruction import by file path.
- Preview/approve workflow before instruction memories are stored.
- Cleaner README, AGY prompts, and installation guidance.

### What it enables

- A coworker can install MemCoder without configuring Ollama.
- A project can import `AGENTS.md`, runbooks, or instruction files as reviewed
  Principles.
- Teams can start testing long-running Remotion workflows.

## Beta-2 — Skills and planning

**Primary goal:** turn validated memory into reusable agent behavior.

```text
Experiences + Principles
→ evidence-backed Skills
→ task-specific Plans
→ verified outcomes improve future Skills
```

### Key work

- Distill validated Principles into reusable Skills.
- Link every Skill to supporting experiences and principles.
- Retrieve Skills with confidence, scope, and provenance.
- Create a lightweight planner that composes Skills into a plan.
- Record whether plans succeeded or failed.
- Add optional LLM-assisted memory intelligence for consolidation, candidate
  reflections/principles, duplicate detection, Skill distillation, and plan
  quality.
- Keep LLM assistance optional; Core remains provider-free.
- Validate on real Remotion workflows with memory/no-memory comparisons.

### What Beta-2 should do

> For a familiar task, the agent retrieves proven project knowledge, selects
> reusable Skills, follows a plan, verifies the result, and learns from the
> outcome.

Beta-2 release gate: show that Skills and plans improve repeated real-world
work without creating memory pollution.

## Beta-3 — Team cognition and Memory Studio

**Goal:** make MemCoder safe and useful across people, agents, and projects.

### Key work

- Shared Experiences, Principles, and Skills.
- Ownership, provenance, permissions, and approval workflows.
- Safe cross-project knowledge transfer.
- Multi-agent coordination around shared plans.
- Conflict handling for contradictory memories.
- A local **Memory Studio** GUI to inspect memory and sources, retrieval traces,
  imported Markdown candidates, Skill evidence, plan outcomes, and team-sharing
  controls.

### What Beta-3 should do

> A team can safely build, inspect, share, and improve durable agent knowledge
> without losing ownership or traceability.

## Version 1.0 — Production-ready cognition layer

**Goal:** make MemCoder stable enough to promise publicly.

### Required before 1.0

- Stable MCP and Python API contracts.
- Reliable database migrations, backups, and upgrades.
- Strong package installation and update flow.
- Reproducible evaluation suite.
- Demonstrated memory-quality and retrieval reliability across real projects.
- Proven Skills and planning value.
- Safe team-sharing boundaries.
- Clear privacy, data-handling, and provider-integration policies.
- Complete documentation and operational guidance.

### What 1.0 can claim

> MemCoder is a dependable, provider-independent cognition layer that helps AI
> agents retain validated knowledge, build reusable Skills, plan work, and
> improve over time.

## Product direction after 1.0

```text
MemCoder Core
→ provider-free local cognition

MemCoder Intelligence
→ optional Claude/other-provider assisted memory quality, Skills, and planning

MemCoder Teams
→ shared cognition, permissions, provenance, and collaboration
```

The central rule through every phase remains the same:

> MemCoder Core must be useful without any model provider. Optional intelligence
> should strengthen the system, never become a hidden dependency.
