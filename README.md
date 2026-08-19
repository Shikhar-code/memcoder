# MemCoder

**Verified memory for coding agents.**

MemCoder gives an AI coding agent a durable record of what was tried, what
passed, and when that result still applies. It retrieves past evidence only
when it can change the next decision, then learns only after the current host
supplies proof.

[![PyPI](https://img.shields.io/pypi/v/memcoder?style=flat-square&label=PyPI&color=334155)](https://pypi.org/project/memcoder/)
[![Python](https://img.shields.io/pypi/pyversions/memcoder?style=flat-square&color=334155)](https://pypi.org/project/memcoder/)
[![License](https://img.shields.io/badge/license-MIT-334155?style=flat-square)](LICENSE)
[![Release](https://img.shields.io/badge/release-0.3.3b1-4f46e5?style=flat-square)](CHANGELOG.md)
[![Core](https://img.shields.io/badge/core-provider--free-0f766e?style=flat-square)](#trust-contract)

[Website](https://memcoder.dev) · [Documentation](#documentation) ·
[Roadmap](docs/roadmap.md) · [Changelog](CHANGELOG.md) ·
[Issues](https://github.com/Shikhar-code/memcoder/issues)

> If MemCoder cannot justify an intervention, it stays silent. If the host
> cannot prove an outcome, MemCoder does not learn it.

## Why it exists

Coding agents are capable inside a task and forgetful across tasks. Typical
memory systems address that by replaying transcripts, summaries, or anything
that looks semantically similar. That creates three problems:

- related context is mistaken for useful guidance;
- plausible output becomes memory before it becomes knowledge; and
- memory consumes more context than it saves.

MemCoder treats memory as evidence, not conversation history. The host model
still reasons, edits, runs tools, and owns the final answer. MemCoder decides
whether prior work deserves attention and whether the new result is strong
enough to retain.

## How it works

```text
new task
  │
  ├─ no applicable evidence ───────────────► host continues normally
  │
  └─ applicable, decision-useful evidence
       │
       ▼
     smallest useful guidance packet
       │
       ▼
     host acts and verifies
       │
       ├─ insufficient proof ──────────────► nothing is learned
       │
       └─ admitted proof
            │
            ├─ durable memory / Skill
            └─ outcome receipt calibrates later retrieval
```

The automatic path is deliberately bounded:

1. **Attend:** decide whether memory is worth injecting at all.
2. **Retrieve:** select trusted evidence that fits the current environment.
3. **Intervene:** return `none`, `risk`, `brief`, or `plan` within a token
   budget.
4. **Verify:** require inspectable host evidence before durable learning.
5. **Calibrate:** record whether guidance was used, changed the action, and
   survived verification.

MemCoder fails open. If it is unavailable or has nothing useful, the host keeps
working without it.

## Quick start

### Install the latest published beta

```powershell
python -m pip install --pre --upgrade memcoder
memcoder setup
memcoder doctor
```

MemCoder requires Python 3.10 or newer. Core cognition does not require a
generation-model API key, Ollama, CUDA, or a cloud account. The first semantic
retrieval may download a local embedding model.

### Install the current source

Use this when the repository is ahead of the published package:

```powershell
git clone https://github.com/Shikhar-code/memcoder.git
cd memcoder
python -m pip install --no-build-isolation .
memcoder doctor
```

Useful first checks:

```powershell
memcoder --help
memcoder storage status
memcoder host-manifest --host codex
```

## Connect a host

Beta 3.2 gives Codex, AGY / Antigravity, and Claude Code the same provider-free
lifecycle, evidence gate, privacy boundary, and fail-open behavior.

| Host | Setup | Verification |
| --- | --- | --- |
| Codex Desktop | Local marketplace plugin | `memcoder doctor --host codex` |
| AGY / Antigravity | `memcoder setup-agy` | `memcoder doctor --host agy` |
| Claude Code | `memcoder setup-claude` | `memcoder doctor --host claude` |
| Any MCP host | Run `python -m adapters.mcp.server` | Inspect `memcoder host-manifest` |

### Codex Desktop

From the cloned repository:

```powershell
python scripts/configure_codex_plugin.py
codex plugin marketplace add .\codex-marketplace
codex plugin add memcoder@memcoder-local
```

Start a new Codex task after installation. The bundled Skill calls the lifecycle
automatically during substantive development work; ordinary users do not need
to mention MemCoder in every prompt.

### AGY / Antigravity

```powershell
memcoder setup-agy
memcoder doctor --host agy
```

Setup changes only the `memcoder` MCP entry, preserves other servers, and binds
AGY to the Python interpreter that ran the command. See the
[AGY integration guide](docs/antigravity_mcp.md).

### Claude Code

Run this from the project Claude should work on:

```powershell
memcoder setup-claude
memcoder doctor --host claude
```

The command installs a project `.mcp.json` entry and an idempotent lifecycle
block in `CLAUDE.md`. Existing project instructions and MCP servers are
preserved. See the [Claude Code guide](docs/claude_code.md).

## The automatic lifecycle

Hosts use one entry point: `autopilot`. A task begins with a stable identifier
and a concise decision frame.

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

After verification, the host closes the same intervention with explicit
outcome fields:

```json
{
  "event": "verification_finished",
  "task_id": "billing-validation-42",
  "problem": "Fix request validation without changing successful responses.",
  "agent_id": "billing-api",
  "outcome": {
    "guidance_used": true,
    "changed_action": true,
    "verification_passed": true,
    "evidence": {
      "checks": [
        {
          "name": "validation regression",
          "kind": "test",
          "status": "passed",
          "command": "python tests/test_validation.py",
          "output": "PASS"
        }
      ]
    },
    "rework_count": 0,
    "host_tokens": 180
  }
}
```

MemCoder closes the prediction as `confirmed`, `ignored`, `contradicted`, or
`inconclusive`. Passing work alone is never interpreted as proof that memory
helped.

## What ships in Beta 3.3

The current release combines three consecutive improvements to the automatic
path.

| Release | What changed | Practical result |
| --- | --- | --- |
| **3.1 — Runtime hardening** | Lazy index startup, strict packet budgets, applicability-first retrieval, normalized evidence, idempotent completion | Faster startup, less irrelevant context, no duplicate learning on retry |
| **3.2 — Host parity** | One versioned lifecycle for Codex, AGY, and Claude Code; setup and certification tools | The same trust contract follows the project across supported hosts |
| **3.3 — Adaptive proof loop** | Explicit outcome closure, privacy-safe prediction receipts, environment-aware calibration | Retrieval adapts from observed outcomes without rewriting trusted evidence |

Release history belongs in the [changelog](CHANGELOG.md); product direction and
release gates belong in the [roadmap](docs/roadmap.md).

## Core capabilities

| Capability | What it does |
| --- | --- |
| **Utility-gated retrieval** | Ranks trusted evidence by applicability, decision value, risk, provenance, and cost; abstains when the packet is not worth injecting. |
| **Project Cortex** | Keeps bounded decisions, rationale, constraints, risks, checkpoints, next actions, resurrection, and verified handoff. |
| **Failure Frontiers** | Surfaces evidence-backed failure mechanisms and the cheapest preventive check before the host repeats them. |
| **Skills and plans** | Promotes verified procedures with preconditions, expected observations, proof, failure handling, rollback, version history, and health. |
| **Cognitive Branches** | Isolates competing hypotheses and changes until their proof obligations pass; supports deterministic diff, merge, and rollback. |
| **Evidence-gated Dreaming** | Proposes local candidate patterns from trusted memories; candidates remain untrusted until sandbox evidence passes. |
| **Replay and contracts** | Compares baseline and memory-assisted receipts and tests cognition behavior deterministically. |
| **Memory Firewall** | Blocks sensitive paths, evaluates local admission policy, and keeps imports untrusted until reviewed. |
| **Outcome calibration** | Tracks whether an exact intervention was useful, ignored, misleading, harmful, or inconclusive in a comparable environment. |
| **Local control plane** | Exposes storage, policy, evidence, replay, Dreaming, and outcome receipts through CLI, Python, MCP, HTTP, and Studio. |

## Trust contract

MemCoder's Core follows a small set of rules:

- **No proof, no durable learning.** A host result must pass deterministic QA.
- **Similarity is not applicability.** Related evidence can still be withheld.
- **Guidance is not authority.** The current host verifies the current project.
- **Ambiguity stays unmeasured.** Success does not imply MemCoder caused it.
- **Evidence is preserved.** Calibration changes ranking, not history.
- **Automatic work is reversible.** Imports, promotions, branches, retention,
  and capsules remain inspectable.
- **Local Core remains useful offline.** Cloud and provider intelligence are not
  hidden requirements.
- **Failure is non-blocking.** A MemCoder error does not stop normal host work.

### What MemCoder stores

| Record | Durable meaning |
| --- | --- |
| **Experience** | Task, environment, action, files, proof, and verified outcome |
| **Reflection** | Concise observation grounded in an approved Experience |
| **Mistake / risk** | Verified failure mode, bad assumption, or negative outcome |
| **Principle** | Transferable guidance with support and applicability limits |
| **Skill** | Versioned procedure with proof and rollback |
| **Project state** | Decisions, constraints, risks, open loops, and next actions |

Task checkpoints, audit events, Dream candidates, and intervention receipts sit
beside semantic memory. Their existence alone never makes them retrievable
guidance. Raw conversations are not the default storage model.

## Memory Studio

The browser fallback runs directly from the Python package:

```powershell
memcoder studio
```

Open `http://127.0.0.1:8765`. Studio provides focused views for memories,
evidence, host receipts, intervention outcomes, replay, Dream candidates, and
policy. The service binds to localhost by default.

The repository also includes a lightweight Tauri desktop shell. It uses plain
HTML, CSS, and JavaScript against the same Python Core—there is no second memory
engine in the UI.

```powershell
cd studio
bun install
bun run dev
```

Build the Windows installer with:

```powershell
bun run build:exe
```

The NSIS installer is written under
`studio/src-tauri/target/release/bundle/nsis/`.

## Interfaces

Every core operation is available through Python, CLI, and MCP. The local HTTP
service exists for desktop and automation adapters.

```python
from memcoder import autopilot_event_cognition

packet = autopilot_event_cognition(
    event="task_started",
    task_id="task-42",
    problem="Fix request validation safely.",
    agent_id="billing-api",
)
```

Common CLI surfaces:

```text
memcoder autopilot          lifecycle entry point
memcoder doctor             local and host diagnostics
memcoder retrieval-debug    ranking, utility, and abstention explanation
memcoder utility-summary    intervention outcome calibration
memcoder project-resurrect  bounded project continuation brief
memcoder project-handoff    privacy-safe cognition capsule
memcoder storage status     durable record and audit counts
memcoder service serve      localhost adapter service
memcoder studio             browser Studio
```

Run `memcoder <command> --help` for exact input requirements.

## Evidence and limits

MemCoder has a narrow controlled transfer result: three baseline AGY runs
passed the visible test but failed private robustness checks; six
MemCoder-assisted runs passed the same private checks. This supports one claim:
in that setup, a verified validation procedure transferred to unseen variants.

It does **not** establish universal improvement across models, repositories, or
tasks. The current Core has deterministic coverage for provider independence,
retrieval safety, QA admission, lifecycle idempotence, host parity, Dreaming,
branch proof gates, and outcome closure. Broad real-project improvement, median
token savings, and production-scale latency remain evaluation targets.

- [Controlled transfer result](docs/beta2_controlled_transfer_results.md)
- [Evaluation protocol](docs/beta2_evaluation_protocol.md)
- [Real-project evaluation protocol](docs/beta2_real_project_evaluation.md)

Current non-goals:

- no claim of consciousness or human-equivalent cognition;
- no silent self-modification of trusted memory;
- no required cloud account or hosted model in Core;
- no team or multi-agent memory in Beta 3.3; and
- no claim that a passing task proves an intervention was helpful.

## Development

Install the repository without build isolation:

```powershell
python -m pip install --no-build-isolation .
python -m memcoder --help
```

Run the focused Beta 3 regression checks:

```powershell
python tests/test_beta31_hardening.py
python tests/test_beta32_host_parity.py
python tests/test_beta33_proof_loop.py
python tests/test_mcp_provider_independence.py
python tests/test_qa_admission.py
python tests/test_retrieval_safety.py
```

The repository intentionally has no provider requirement for these checks.

## Documentation

| Document | Purpose |
| --- | --- |
| [Product and research roadmap](docs/roadmap.md) | Release sequence, gates, and long-range research |
| [Changelog](CHANGELOG.md) | Version-by-version implementation history |
| [AGY / Antigravity integration](docs/antigravity_mcp.md) | Setup, lifecycle, and certification |
| [Claude Code integration](docs/claude_code.md) | Project setup and automatic lifecycle |
| [AGY prompt template](docs/antigravity_prompt_template.md) | Guarded manual host instructions |
| [Architecture PDF](output/pdf/memcoder-current-architecture.pdf) | Component-level design |
| [Evaluation protocol](docs/beta2_evaluation_protocol.md) | Controlled comparison methodology |

## Project status

MemCoder is beta software. Back up local cognition before testing migrations or
new storage behavior:

```powershell
memcoder storage backup
```

Bug reports and reproducible negative results are welcome through
[GitHub Issues](https://github.com/Shikhar-code/memcoder/issues).

## License

[MIT](LICENSE) © Shikhar-code
