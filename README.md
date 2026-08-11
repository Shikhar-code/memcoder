<div align="center">

<img src="assets/memcoder-hero-beta2.svg" alt="MemCoder - verified cognition for coding agents" width="100%" />

<br />

<a href="https://pypi.org/project/memcoder/"><img src="https://img.shields.io/pypi/v/memcoder?style=for-the-badge&label=PyPI&color=6D9EFF" alt="PyPI" /></a>
<a href="https://pypi.org/project/memcoder/"><img src="https://img.shields.io/pypi/pyversions/memcoder?style=for-the-badge&color=63D7C5" alt="Python 3.10+" /></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-BFA1FF?style=for-the-badge" alt="MIT license" /></a>
<a href="docs/roadmap.md"><img src="https://img.shields.io/badge/status-Beta%202.5-FFB86B?style=for-the-badge" alt="Beta 2.5" /></a>

### Persistent cognition for agents that have to be right twice.

**MemCoder is local, provider-independent memory for coding agents.**

It brings back verified evidence only when it can improve the next decision,
then learns only after the host proves the result.

<sub>Local-first | evidence-gated | token-aware | host-agnostic</sub>

<br />

<a href="#quick-start"><strong>Quick start</strong></a>
&nbsp;|&nbsp; <a href="#what-it-actually-does"><strong>What it does</strong></a>
&nbsp;|&nbsp; <a href="#beta-25"><strong>Beta 2.5</strong></a>
&nbsp;|&nbsp; <a href="#connect-your-host"><strong>Connect a host</strong></a>
&nbsp;|&nbsp; <a href="#proof-not-promises"><strong>Evidence</strong></a>

</div>

---

> **Most agent memory remembers things. MemCoder makes reuse accountable.**
>
> It can stay silent, flag a known failure, offer a compact brief, or compile a
> bounded plan. Either way, the host still owns the code, tools, and proof.

<table>
<tr>
<td width="33%" valign="top">

### Remember proof

Keep verified outcomes, not raw conversations. An Experience carries the task,
solution, files, and evidence that made it trustworthy.

</td>
<td width="33%" valign="top">

### Spend attention

Related is not enough. MemCoder checks utility, risk, provenance, and token
cost before it interrupts a task.

</td>
<td width="34%" valign="top">

### Get better safely

Turn repeated, verified work into Skills with preconditions, verification,
rollback, version history, and causal credit.

</td>
</tr>
</table>

## What it actually does

<p align="center">
  <img src="assets/memcoder-cognition-rail.svg" alt="Task to utility gate to guidance to verification to learning" width="100%" />
</p>

The host does the work. MemCoder controls the cognitive context around it.

| Moment | MemCoder action | Why it matters |
| --- | --- | --- |
| Before work | Retrieves only decision-useful verified evidence | No transcript dump, no generic advice flood |
| Before risk | Surfaces the cheapest check for destructive, migration, dependency, release, or security work | Known failures become preventable |
| During work | Keeps bounded task and project state | A long project can resume without replaying chat |
| After proof | Admits only QA-approved evidence | A passing result can compound; a failed claim cannot |
| Next time | Transfers Skills with assumptions and rollback visible | Reuse is inspectable instead of magical |

<details>
<summary><strong>Show the decision loop</strong></summary>

```text
task_started
  -> utility gate: none / risk / brief / plan
  -> host investigates and acts
  -> focused verification
  -> QA admission
  -> durable memory only when proof exists
```

If no memory changes the next action, MemCoder deliberately returns `none`.
That restraint is a feature, not an empty result.

</details>

## Quick start

### 1. Install

```powershell
pip install memcoder
memcoder --help
memcoder storage status
```

**Requirements:** Python 3.10+. The first semantic-index run can download a
local embedding model. The core runtime does not require Ollama, CUDA, or a
model API key.

<details>
<summary><strong>Use the current source instead</strong></summary>

```powershell
git clone https://github.com/Shikhar-code/memcoder.git
cd memcoder
python -m pip install --no-build-isolation .
python -m memcoder --help
```

Use this route for Beta development or the local Codex plugin.

</details>

### 2. Let an agent use it

`lifecycle.json`

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
memcoder autopilot --input lifecycle.json
```

That one call returns the smallest useful intervention plus a verification
plan. The host continues normally if MemCoder is unavailable.

## Beta 2.4

<table>
<tr>
<td width="50%" valign="top">

### Invisible Autopilot

Normal prompts can trigger provider-neutral lifecycle events:

`task_started` -> `before_edit` -> `before_tool` -> `verification_finished`

The attention governor deduplicates unchanged tasks, chooses the smallest
intervention, and fails open so cognition never blocks the host.

</td>
<td width="50%" valign="top">

### Skill Intelligence

Skills are now small, versioned programs rather than saved advice. They carry
preconditions, steps, expected observations, verification, failure handling,
rollback, limits, and evidence.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### Failure Radar + proof planning

Before high-cost actions, MemCoder names the failure mechanism and the
cheapest native check. A command passing is not confused with proving the
requested behavior.

</td>
<td width="50%" valign="top">

### Token Economy

The lifecycle ledger tracks injected cognition, repeated context avoided, and
the estimated net token dividend. Context is earned, not assumed.

</td>
</tr>
</table>

<details>
<summary><strong>Open the Beta 2.4 control panel</strong></summary>

| Control | What it gives you |
| --- | --- |
| `memcoder autopilot` | One fail-open lifecycle entry point |
| `memcoder autopilot-control` | `pause`, `resume`, `inspect`, and `rollback` |
| `memcoder token-ledger` | Per-task cognition and token accounting |
| `memcoder skill-compile` | Reusable steps vs assumptions requiring adaptation |
| `memcoder skill-compose` | A compatible composition or explicit conflict |
| `memcoder skill-evolve` | A reviewable next Skill version with history intact |
| `memcoder skill-credit` | Influence evidence separate from mere Skill presence |

Automatic capture remains QA-gated and reversible. It never treats a stopped
host as a successful outcome.

</details>

## Beta 2.5

<table>
<tr>
<td width="50%" valign="top">

### Automatic Dreaming

After a QA-approved task, MemCoder quietly compares verified episodes and
creates compact candidate insights. No manual Dream command is required.
Candidates stay local, versioned, and outside trusted retrieval until they
survive sandbox evidence.

</td>
<td width="50%" valign="top">

### Cognition Contracts

Hosts can assert cognitive behavior in deterministic tests: require proof,
abstain without evidence, exclude non-trusted records, and fail open when the
adapter is unavailable.

</td>
</tr>
</table>

```text
verified outcome
  -> automatic Dream candidate
  -> held-out / sandbox checks
  -> provisional or rejected
  -> reversible trusted Principle (only after proof)
```

<details>
<summary><strong>Open the Beta 2.5 control panel</strong></summary>

| Control | What it gives you |
| --- | --- |
| `memcoder dream --input dream.json` | Run or inspect local Dream candidates |
| `memcoder dream --input request.json` with `action=verify` | Supply sandbox evidence and optionally promote a candidate |
| `memcoder dream --input request.json` with `action=rollback` | Reversibly roll back a candidate and any promoted record |
| `memcoder contract` | Evaluate a versioned deterministic cognition contract |
| `memcoder host-certify` | Check lifecycle, QA, and fail-open host receipts |
| `memcoder evaluate` with `condition=dreaming` | Compare Dreaming against a matched baseline |

Dreaming is automatic by default. It never silently overwrites trusted memory;
promotion requires inspectable sandbox evidence and remains reversible.

</details>

## Connect your host

Pick the door you already use. The cognition model stays the same.

<table>
<tr>
<td width="33%" valign="top">

### Codex Desktop

The local plugin invokes MemCoder automatically for substantive engineering
work. No special end-user prompt is required after setup.

```powershell
git clone https://github.com/Shikhar-code/memcoder.git
cd memcoder
python -m pip install --no-build-isolation .
python scripts/configure_codex_plugin.py
```

Then add `codex-marketplace` as a local marketplace in **Codex > Plugins**,
install **MemCoder**, and restart Codex.

</td>
<td width="33%" valign="top">

### AGY / Antigravity

```powershell
python -m memcoder setup-agy
```

Restart AGY. For manual workflows, first retrieve a compact intervention,
then solve and verify in a follow-up request. See the
[AGY prompt template](docs/antigravity_prompt_template.md).

</td>
<td width="34%" valign="top">

### Python, MCP, or automation

Every operation accepts structured JSON through the CLI, Python API, or MCP.

```python
from memcoder import autopilot_event_cognition

packet = autopilot_event_cognition(
    event="task_started",
    task_id="task-42",
    problem="Fix request validation safely.",
    agent_id="billing-api",
)
```

</td>
</tr>
</table>

## The memory contract

MemCoder stores different things for different jobs. None of them is a raw
conversation archive.

| Layer | It contains | It never becomes |
| --- | --- | --- |
| Experience | Verified task, solution, files, evidence | Unproven narrative |
| Reflection | Short investigation observation | A fix disguised as self-critique |
| Principle | Transferable evidence-backed guidance | Generic motivational advice |
| Skill | A promoted, test-carrying procedure | Open-ended autonomy |
| Project Cortex | Facts, rationale, risks, and next actions | A full transcript dump |

### The rules that keep it honest

- **Local-first:** cognition stays on the machine by default.
- **Evidence-gated:** durable learning needs inspectable host verification.
- **Provenance-aware:** guidance keeps its source and current validity state.
- **Reversible:** contradiction, retention, and automatic capture preserve or
  deprecate evidence; they do not silently erase history.
- **Provider-independent:** no generation provider is required for the core.

<details>
<summary><strong>Import project instructions without polluting Experience memory</strong></summary>

MemCoder can preview actionable guidance from `AGENTS.md`, runbooks, and
architecture Markdown. It imports only approved instructions as Principles;
documentation does not pretend to be lived, verified Experience.

```json
{
  "file_path": "AGENTS.md",
  "agent_id": "billing-api",
  "approve": false
}
```

Review the preview, then repeat with `approve: true`. Files must be UTF-8
Markdown inside the launched project and no larger than 1 MB.

</details>

## Proof, not promises

In the controlled transfer evaluation, three baseline AGY runs passed visible
tests but failed private robustness checks. Six valid MemCoder-assisted runs
passed the same private checks.

That supports one narrow claim: **verified validation procedures transferred to
unseen variants in that controlled setup.** It does not prove universal agent
improvement.

Beta 2.5 also has provider-free evidence for automatic Dreaming, sandbox
promotion, rollback, Cognition Contracts, and host certification. A new
baseline-versus-Dreaming host comparison is intentionally **not** claimed yet:
the required clean sessions and receipts are not present in this checkout.
See the [Beta 2.5 evaluation record](docs/beta25_evaluation_results.md) for
the exact boundary between verified implementation behavior and pending
developer-outcome evidence.

| Ready now | Still being measured |
| --- | --- |
| Provider-free local runtime | Broad real-project causal improvement |
| QA-gated learning and retrieval safety | Median token and rework reduction |
| Utility Engine and Project Cortex | Failure interception across diverse repositories |
| Lifecycle Autopilot, Skill Intelligence, and automatic Dreaming safety | Matched baseline/Dreaming host outcomes and production-scale latency |

- [Controlled transfer results](docs/beta2_controlled_transfer_results.md)
- [Evaluation protocol](docs/beta2_evaluation_protocol.md)
- [Real-project evaluation protocol](docs/beta2_real_project_evaluation.md)
- [Beta 2.5 evaluation record](docs/beta25_evaluation_results.md)
- [Roadmap](docs/roadmap.md)

## For developers who want the wiring

<details>
<summary><strong>CLI workflow</strong></summary>

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
<summary><strong>Project continuity</strong></summary>

```powershell
memcoder project-update --input project-update.json
memcoder project-resurrect --input project-resurrect.json
memcoder project-handoff --input project-handoff.json
memcoder project-accept --input project-accept.json
```

Project Cortex stores bounded decisions and state. Resurrection reports
environment drift instead of treating stale state as truth.

</details>

<details>
<summary><strong>Storage and development checks</strong></summary>

```powershell
python -m pip install --no-build-isolation .
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
python tests/test_utility_engine.py
python tests/test_project_cortex.py
python tests/test_beta23_cli.py
python tests/test_autopilot.py
python tests/test_skill_intelligence.py
python tests/test_beta24_cli.py
```

</details>

## Documentation

| Document | Use it for |
| --- | --- |
| [Roadmap](docs/roadmap.md) | Product direction and quantitative release gates |
| [Changelog](CHANGELOG.md) | Release-facing changes and compatibility notes |
| [MCP integration](docs/antigravity_mcp.md) | MCP behavior and provider independence |
| [AGY prompt template](docs/antigravity_prompt_template.md) | Guarded AGY workflow |
| [Architecture PDF](output/pdf/memcoder-current-architecture.pdf) | Component-level design |

## License

Released under the [MIT License](LICENSE).

<div align="center">

### Retrieve precisely. Decide deliberately. Learn from proof.

<sub>Built by <a href="https://github.com/Shikhar-code">Shikhar-code</a>.</sub>

</div>
