<div align="center">

<img src="assets/memcoder-hero-beta2.svg" alt="MemCoder Beta 2.5 — local, evidence-gated cognition for coding agents" width="100%" />

<br />

<a href="https://pypi.org/project/memcoder/"><img src="https://img.shields.io/pypi/v/memcoder?style=for-the-badge&label=PyPI&color=6D9EFF" alt="PyPI" /></a>
<a href="https://pypi.org/project/memcoder/"><img src="https://img.shields.io/pypi/pyversions/memcoder?style=for-the-badge&color=63D7C5" alt="Python 3.10+" /></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-BFA1FF?style=for-the-badge" alt="MIT license" /></a>
<a href="docs/roadmap.md"><img src="https://img.shields.io/badge/status-Beta%202.5-FFB86B?style=for-the-badge" alt="Beta 2.5" /></a>

### Persistent cognition for agents that need to be right twice.

MemCoder is a local, provider-independent trust layer for coding agents. It
retrieves verified context only when it can change a decision, then learns only
after the host supplies proof.

<sub>Local-first · evidence-gated · fail-open · token-aware · host-agnostic</sub>

<br />

<a href="#start-here"><strong>Start here</strong></a>
&nbsp;·&nbsp; <a href="#why-memcoder"><strong>Why MemCoder</strong></a>
&nbsp;·&nbsp; <a href="#whats-new-in-beta-25"><strong>Beta 2.5</strong></a>
&nbsp;·&nbsp; <a href="#connect-a-host"><strong>Connect a host</strong></a>
&nbsp;·&nbsp; <a href="#evidence-not-hype"><strong>Evidence</strong></a>

</div>

---

> Most agent memory systems remember text. MemCoder remembers **what was
> verified**, **why it mattered**, and **when it should stay silent**.

## Why MemCoder

Coding agents lose the thread across long projects. They repeat known mistakes,
re-read too much context, and can mistake a plausible answer for a proven one.
MemCoder sits beside the host model rather than replacing it:

| The host owns | MemCoder owns |
| --- | --- |
| Reasoning, editing, tools, and final verification | Trusted memory, retrieval restraint, reusable procedures, and learning admission |
| The code change | Whether earlier evidence is useful enough to surface |
| The final answer | Whether the outcome has enough proof to become durable memory |

This means a host can keep working normally when MemCoder has nothing useful to
add—or when MemCoder is temporarily unavailable.

## The loop

<p align="center">
  <img src="assets/memcoder-cognition-rail.svg" alt="Task to utility gate to guidance to verification to learning" width="100%" />
</p>

| Moment | MemCoder does | Result |
| --- | --- | --- |
| Before work | Retrieves only decision-useful, trusted evidence | No transcript dump or advice flood |
| Before risk | Names the likely failure mechanism and cheapest proof | Known mistakes become preventable |
| During work | Preserves bounded decisions, constraints, and next actions | Long projects resume without replaying chat |
| After proof | Runs QA before it admits learning | A claim without evidence does not become memory |
| Between tasks | Reuses Skills and creates sandboxed Dream candidates | Learning compounds without silently mutating trust |

## Start here

### Install the published package

```powershell
python -m pip install --pre memcoder
python -m memcoder --help
python -m memcoder storage status
```

MemCoder requires Python 3.10+. Its core does not require Ollama, CUDA, or a
generation-model API key. The first semantic-index use may download a local
embedding model.

### Use the current Beta 2.5 source

```powershell
git clone https://github.com/Shikhar-code/memcoder.git
cd memcoder
python -m pip install --no-build-isolation .
python -m memcoder --help
```

### Give a host one automatic entry point

Create `task.json`:

```json
{
  "event": "task_started",
  "task_id": "billing-validation-42",
  "problem": "Fix request validation without changing successful responses.",
  "agent_id": "billing-api",
  "environment": {
    "branch": "main",
    "available_checks": ["python tests/test_validation.py"]
  }
}
```

```powershell
memcoder autopilot --input task.json
```

The response is deliberately small: `none`, `risk`, `brief`, or `plan`, plus
the cheapest verification requirement. The host remains in control.

## What is in the current core

<table>
<tr>
<td width="50%" valign="top">

### Useful memory, not more memory

The Utility Engine ranks trusted evidence by relevance, risk, provenance, and
decision value. Related-but-unhelpful records are withheld.

</td>
<td width="50%" valign="top">

### Skills with boundaries

Promoted Skills carry preconditions, expected observations, verification,
failure handling, rollback, version history, and influence evidence.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### Autopilot and Failure Radar

Lifecycle events deduplicate unchanged work, flag preventable risk, recommend
the cheapest check, and fail open when the adapter cannot help.

</td>
<td width="50%" valign="top">

### Project Cortex

MemCoder keeps bounded project state: decisions, rationale, risks, drift,
resurrection, and safe handoff—never a raw chat archive.

</td>
</tr>
</table>

<details>
<summary><strong>What MemCoder stores</strong></summary>

| Layer | Purpose | Never treated as |
| --- | --- | --- |
| Experience | Verified task, solution, files, and evidence | A raw conversation |
| Reflection | A concise investigation observation | A fix disguised as insight |
| Principle | Transferable, evidence-backed guidance | Generic motivation |
| Skill | A test-carrying reusable procedure | Open-ended autonomy |
| Project Cortex | Decisions, constraints, risks, and next actions | A transcript dump |

</details>

## What's new in Beta 2.5

Beta 2.5 is the current release line. It adds a controlled way for memory to
improve between verified tasks without turning “self-improvement” into silent,
unreviewable behavior.

<table>
<tr>
<td width="50%" valign="top">

### Automatic Dreaming

After a QA-approved outcome, MemCoder compares related trusted Experiences and
creates a compact candidate pattern. Candidates include source evidence and
counterexamples, stay local, and are excluded from trusted retrieval.

</td>
<td width="50%" valign="top">

### Sandbox before promotion

A Dream candidate needs structured, passed sandbox evidence before it can be
promoted. Promotion is inspectable and reversible; failed or incomplete
candidates remain quarantined.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### Cognition Contracts

Repositories can test the cognitive layer in CI: require verification, abstain
without evidence, exclude non-trusted records, and preserve fail-open host
behavior.

</td>
<td width="50%" valign="top">

### Host certification

Host receipts can be checked for lifecycle boundaries, QA-gated learning,
privacy behavior, and fallback safety before you trust an integration.

</td>
</tr>
</table>

```text
verified outcome
  -> automatic Dream candidate
  -> sandbox evidence
  -> promoted Principle or rejected candidate
  -> reversible provenance-backed learning
```

<details>
<summary><strong>Beta 2.5 controls</strong></summary>

| Command | Use it for |
| --- | --- |
| `memcoder dream --input request.json` | Inspect, verify, promote, or roll back Dream candidates |
| `memcoder contract --input request.json` | Run deterministic cognition assertions |
| `memcoder host-certify --input request.json` | Validate a host’s lifecycle and evidence receipts |
| `memcoder evaluate --input runs.json` | Compare matched host conditions, including `dreaming` |
| `memcoder storage status` | Inspect local memory and Dream-candidate storage |

</details>

## Connect a host

### Codex Desktop

The included **MemCoder Codex plugin** invokes the lifecycle automatically for
substantive engineering work. You do not need to write a MemCoder-specific
prompt every time.

```powershell
git clone https://github.com/Shikhar-code/memcoder.git
cd memcoder
python -m pip install --no-build-isolation .
python scripts/configure_codex_plugin.py
```

In Codex, add `codex-marketplace` as a local marketplace, install **MemCoder**,
then restart Codex. After source updates, refresh/reinstall the MemCoder plugin
so Codex loads its latest skill instructions.

### AGY / Antigravity

```powershell
python -m memcoder setup-agy
```

Restart AGY. The [AGY prompt template](docs/antigravity_prompt_template.md)
explains the manual path; the MCP adapter remains provider-free.

### Python, MCP, and automation

Every operation is available through structured Python, CLI, and MCP calls.

```python
from memcoder import autopilot_event_cognition

packet = autopilot_event_cognition(
    event="task_started",
    task_id="task-42",
    problem="Fix request validation safely.",
    agent_id="billing-api",
)
```

## Evidence, not hype

MemCoder has a controlled transfer result: three baseline AGY runs passed the
visible test but failed private robustness checks; six MemCoder-assisted runs
passed the same private checks. That supports a narrow claim that verified
validation procedures transferred to unseen variants in that setup.

It does **not** prove that MemCoder universally improves every model, task, or
repository. Beta 2.5’s automatic Dreaming, sandbox, rollback, contract, and
host-certification behavior is verified provider-free. A clean real-host
baseline-versus-Dreaming comparison is still pending.

| Verified now | Still being measured |
| --- | --- |
| Provider-free local runtime and fail-open host behavior | Broad real-project performance improvement |
| QA-gated learning, retrieval safety, and reversible Dreaming | Median token and rework reduction |
| Skills, Project Cortex, and cognition contracts | Production-scale latency and cloud operation |

- [Controlled transfer result](docs/beta2_controlled_transfer_results.md)
- [Beta 2.5 evaluation record](docs/beta25_evaluation_results.md)
- [Evaluation protocol](docs/beta2_evaluation_protocol.md)
- [Real-project evaluation protocol](docs/beta2_real_project_evaluation.md)

### Why the Beta 2.5 evaluation record exists

[`beta25_evaluation_results.md`](docs/beta25_evaluation_results.md) is a
transparency document, not a runtime feature. It records exactly what was
verified in this checkout and what was **not** measured yet. Its purpose is to
prevent the README or release notes from turning passing unit tests into an
unsupported claim that Dreaming improves all agents.

## Developer reference

<details>
<summary><strong>Manual CLI workflow</strong></summary>

```powershell
memcoder intervene --input task.json
memcoder verify --input outcome.json
memcoder record --input outcome.json
memcoder retrieval-debug --input task.json
memcoder storage status
```

`verify` is read-only. `record` reruns the QA gate and stores nothing when
evidence is failed or insufficient.

</details>

<details>
<summary><strong>Project continuity commands</strong></summary>

```powershell
memcoder project-update --input project-update.json
memcoder project-resurrect --input project-resurrect.json
memcoder project-handoff --input project-handoff.json
memcoder project-accept --input project-accept.json
```

</details>

<details>
<summary><strong>Provider-free regression checks</strong></summary>

```powershell
python tests/test_automation_cli.py
python tests/test_mcp_provider_independence.py
python tests/test_retrieval_safety.py
python tests/test_memory_quality.py
python tests/test_qa_admission.py
python tests/test_cognition_brief.py
python tests/test_skill_promotion.py
python tests/test_planning.py
python tests/test_skill_health.py
python tests/test_evaluation.py
python tests/test_dreaming.py
python tests/test_cognition_contracts.py
python tests/test_beta25_cli.py
```

</details>

## Explore further

| Document | Start here when you need |
| --- | --- |
| [Roadmap](docs/roadmap.md) | Product direction and release gates |
| [Changelog](CHANGELOG.md) | Version-by-version changes |
| [MCP integration](docs/antigravity_mcp.md) | Provider-free MCP behavior |
| [AGY prompt template](docs/antigravity_prompt_template.md) | Guarded AGY use |
| [Architecture PDF](output/pdf/memcoder-current-architecture.pdf) | Component-level design |

## License

Released under the [MIT License](LICENSE).

<div align="center">

### Retrieve precisely. Decide deliberately. Learn from proof.

<sub>Built by <a href="https://github.com/Shikhar-code">Shikhar-code</a>.</sub>

</div>
