<p align="center">
  <img src="https://raw.githubusercontent.com/Shikhar-code/memcoder/main/assets/memcoder-hero.svg" alt="MemCoder — verified memory for coding agents" width="100%" />
</p>

<p align="center">
  <a href="https://pypi.org/project/memcoder/"><img src="https://img.shields.io/pypi/v/memcoder?style=flat-square&label=PyPI&color=3b6fb6" alt="PyPI release" /></a>
  <a href="https://pypi.org/project/memcoder/"><img src="https://img.shields.io/pypi/pyversions/memcoder?style=flat-square&color=287b62" alt="Supported Python versions" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-5b6570?style=flat-square" alt="MIT license" /></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/release-0.3.5b1-b06f20?style=flat-square" alt="Beta 3.5" /></a>
  <a href="#the-trust-model"><img src="https://img.shields.io/badge/core-provider--free-287b62?style=flat-square" alt="Provider-free core" /></a>
</p>

<p align="center">
  <strong>Give an agent continuity without teaching it to trust guesses.</strong>
</p>

<p align="center">
  <a href="https://memcoder.dev">Website</a> ·
  <a href="#install">Install</a> ·
  <a href="#connect-a-host">Connect a host</a> ·
  <a href="docs/roadmap.md">Roadmap</a> ·
  <a href="CHANGELOG.md">Changelog</a>
</p>

---

MemCoder is a local cognition layer for coding agents. It keeps verified
experience, retrieves it only when it can change the next decision, and refuses
to learn from an outcome the host cannot prove.

> **One rule governs the system:** no proof, no durable learning.

## The point

Coding agents are capable inside a task and forgetful across tasks. Most memory
systems compensate by replaying transcripts, summaries, or anything that looks
similar. More context arrives, but not necessarily more truth.

MemCoder takes a narrower position:

| The coding agent owns | MemCoder owns |
| --- | --- |
| Reasoning, edits, tools, and the final answer | Trusted memory, restrained retrieval, and learning admission |
| The current implementation | Whether older evidence applies to the current environment |
| Verification of the result | Whether that proof is strong enough to retain |

The host remains fully usable without MemCoder. When no memory earns its place,
MemCoder returns nothing and gets out of the way.

<p align="center">
  <img src="https://raw.githubusercontent.com/Shikhar-code/memcoder/main/assets/memcoder-decision-gate.svg" alt="The MemCoder utility gate" width="100%" />
</p>

## Install

### Published beta

```powershell
python -m pip install --pre --upgrade memcoder
memcoder setup --all
memcoder doctor
```

MemCoder requires Python 3.10 or newer. Its core does not require a generation
model, cloud account, Ollama, CUDA, or provider API key. Persistent MCP hosts
warm the optional local semantic model after startup; task requests use the
SQLite lexical path immediately and never wait for a cold model download.

### Current source

Use this when the repository is ahead of PyPI:

```powershell
git clone https://github.com/Shikhar-code/memcoder.git
cd memcoder
python -m pip install --no-build-isolation .
python -m memcoder doctor
```

Check the available surfaces:

```powershell
memcoder --help
memcoder storage status
memcoder host-manifest --host codex
```

## The proof loop

MemCoder participates at task boundaries rather than narrating over the agent.
At the start, it may return `none`, `risk`, `brief`, or `plan`. At the end, the
host supplies evidence. Only admitted evidence can create durable learning.

<p align="center">
  <img src="https://raw.githubusercontent.com/Shikhar-code/memcoder/main/assets/memcoder-proof-loop.svg" alt="The evidence-gated MemCoder lifecycle" width="100%" />
</p>

| Boundary | MemCoder does | MemCoder does not do |
| --- | --- | --- |
| Task starts | Checks applicability, utility, risk, provenance, and context cost | Dump related memories into the prompt |
| Risk changes | Surfaces a known failure mechanism and its cheapest preventive check | Treat an old fix as proof for this repository |
| Host verifies | Evaluates the supplied checks, files, assertions, or review evidence | Infer success from a confident answer |
| Task closes | Records an outcome receipt and calibrates later retrieval | Rewrite trusted history because one run passed |

<details>
<summary><strong>See the lifecycle payloads</strong></summary>

Start a task:

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

Close it after verification:

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
      "checks": [{
        "name": "validation regression",
        "kind": "test",
        "status": "passed",
        "command": "python tests/test_validation.py",
        "output": "PASS"
      }]
    },
    "rework_count": 0,
    "host_tokens": 180
  }
}
```

The resulting prediction receipt is `confirmed`, `ignored`, `contradicted`, or
`inconclusive`. Passing work alone never proves that memory caused the result.

</details>

## What becomes memory

MemCoder does not use raw conversation history as its default storage model. A
durable record joins a claim to its proof, operating environment, applicability
limits, and current validity.

<p align="center">
  <img src="https://raw.githubusercontent.com/Shikhar-code/memcoder/main/assets/memcoder-memory-anatomy.svg" alt="The anatomy of a durable MemCoder record" width="100%" />
</p>

| Record | Durable meaning |
| --- | --- |
| **Experience** | A task, environment, action, affected files, proof, and verified outcome |
| **Reflection** | A concise observation grounded in an approved Experience |
| **Mistake / risk** | A verified failure mode, bad assumption, or negative outcome |
| **Principle** | Transferable guidance with supporting evidence and applicability limits |
| **Skill** | A versioned procedure with preconditions, observations, proof, failure handling, and rollback |
| **Project state** | Decisions, rationale, constraints, risks, open loops, and next actions |

Checkpoints, audit events, Dream candidates, and intervention receipts live
beside semantic memory. Their existence alone does not make them trusted or
retrievable.

## Connect a host

Codex Desktop, AGY / Antigravity, and Claude Code use the same versioned,
provider-free lifecycle. Host adapters cannot weaken the evidence gate.

<p align="center">
  <img src="https://raw.githubusercontent.com/Shikhar-code/memcoder/main/assets/memcoder-host-parity.svg" alt="One MemCoder lifecycle across coding hosts" width="100%" />
</p>

| Host | Setup | Verify |
| --- | --- | --- |
| **Codex Desktop** | Install the local marketplace plugin | `memcoder doctor --host codex` |
| **AGY / Antigravity** | `memcoder setup-agy` | `memcoder doctor --host agy` |
| **Claude Code** | `memcoder setup-claude` | `memcoder doctor --host claude` |
| **Any MCP host** | Run `python -m adapters.mcp.server` | Inspect `memcoder host-manifest` |

Configure every host MemCoder can safely configure from Python with one
idempotent command:

```powershell
memcoder setup --all
```

It preserves unrelated MCP servers, backs up changed JSON configuration,
installs Claude's lifecycle instructions, and reports that Codex remains
managed by its marketplace plugin.

### Codex Desktop

From the cloned repository:

```powershell
python scripts/configure_codex_plugin.py
codex plugin marketplace add .\codex-marketplace
codex plugin add memcoder@memcoder-local
```

Start a new Codex task after installation. The bundled Skill invokes the
lifecycle automatically during substantive development; no MemCoder-specific
prompt is required.

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

## What ships in Beta 3.5

Beta 3.5 is the final beta and the 1.0 qualification line. It retains the
bounded 3.4 runtime and makes its useful path dependable, actionable, and
measurable:

| Release | Engineering change | Practical result |
| --- | --- | --- |
| **3.1 — Runtime hardening** | Lazy index startup, strict packet budgets, applicability-first retrieval, normalized evidence, idempotent completion | Faster startup, less irrelevant context, no duplicate learning on retry |
| **3.2 — Host parity** | One lifecycle contract for Codex, AGY, and Claude Code; setup and certification tools | The same trust boundary follows a project across supported hosts |
| **3.3 — Adaptive proof loop** | Explicit outcome closure, privacy-safe prediction receipts, environment-aware calibration | Retrieval adapts from observed outcomes without rewriting trusted evidence |
| **3.4 — Bounded Autopilot** | Attention gating, empty-store short-circuiting, hard intervention deadlines, circuit breaking, bounded embedding cache, lifecycle telemetry | Ordinary hosts stay fast and fail open; slow or empty retrieval cannot hijack the task |
| **3.5 — Release-grade cognition** | SQLite FTS5 retrieval with a bounded SQL fallback, background semantic prewarming, actionable decision cards, additive schema backup and validation, release-gate evaluation | MemCoder returns an applicable action with limits and proof—or abstains quickly without blocking the host |

Measure the provider-free boundary without touching your stored memory:

```powershell
memcoder benchmark --iterations 5
memcoder storage upgrade --dry-run
memcoder storage upgrade
```

For a host-specific budget, set `MEMCODER_INTERVENTION_TIMEOUT_MS` (default
1500 ms). `MEMCODER_CIRCUIT_COOLDOWN_SECONDS` controls the timeout cooldown and
`MEMCODER_EMBED_CACHE_SIZE` bounds the in-process embedding cache; all three
controls are clamped to safe ranges.

Release history lives in the [changelog](CHANGELOG.md). Product direction and
release gates live in the [roadmap](docs/roadmap.md).

## Capability index

| Capability | Purpose |
| --- | --- |
| **Dependable local retrieval** | Search durable SQLite memory first, use FTS5 when available, and reserve semantic reranking for an already-warm persistent host |
| **Decision cards** | State the action, applicability limit, avoided failure, evidence, and cheapest verification for the selected memory |
| **Bounded Autopilot** | Gate attention before retrieval, enforce a host deadline, and fail open through a short circuit cooldown |
| **Utility-gated retrieval** | Rank trusted evidence by fit, decision value, risk, provenance, and cost; abstain when a packet is not worth injecting |
| **Project Cortex** | Preserve bounded decisions, rationale, constraints, risks, checkpoints, resurrection, and verified handoff |
| **Failure Frontiers** | Surface evidence-backed failure mechanisms and the cheapest preventive check before they repeat |
| **Skills and plans** | Promote verified procedures with explicit limits, proof, failure handling, rollback, version history, and health |
| **Cognitive Branches** | Isolate competing hypotheses until their proof obligations pass; then diff, merge, or roll back |
| **Evidence-gated Dreaming** | Propose local candidate patterns from trusted memories while keeping them untrusted until sandbox proof passes |
| **Replay and contracts** | Compare baseline and memory-assisted receipts and test cognition behavior deterministically |
| **Memory Firewall** | Block sensitive paths, enforce local admission policy, and keep imports untrusted until reviewed |
| **Outcome calibration** | Track whether an exact intervention was helpful, ignored, misleading, harmful, or inconclusive in a comparable environment |

## The trust model

MemCoder Core follows a deliberately small contract:

- **No proof, no durable learning.** Host evidence must pass deterministic QA.
- **Similarity is not applicability.** Related evidence may still be withheld.
- **Guidance is not authority.** The current host verifies the current project.
- **Ambiguity stays unmeasured.** Success does not imply MemCoder caused it.
- **Evidence is preserved.** Calibration changes ranking, not history.
- **Automatic work is reversible.** Imports, promotions, branches, retention,
  and capsules remain inspectable.
- **Local Core remains useful offline.** Cloud and provider intelligence are not
  hidden requirements.
- **Failure is non-blocking.** A MemCoder error does not stop normal host work.

## Memory Studio

Run the browser fallback directly from the Python package:

```powershell
memcoder studio
```

Open `http://127.0.0.1:8765`. Studio exposes memories, evidence, host receipts,
intervention outcomes, replay, Dream candidates, and policy. It binds to
localhost by default.

The repository also includes a lightweight Tauri desktop shell. It uses plain
HTML, CSS, and JavaScript against the same Python Core—there is no second memory
engine in the interface.

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

Core operations are available through Python, CLI, MCP, and the local HTTP
service used by desktop and automation adapters.

```python
from memcoder import autopilot_event_cognition

packet = autopilot_event_cognition(
    event="task_started",
    task_id="task-42",
    problem="Fix request validation safely.",
    agent_id="billing-api",
)
```

```text
memcoder autopilot          lifecycle entry point
memcoder benchmark          provider-free latency and timeout check
memcoder doctor             local and host diagnostics
memcoder retrieval-debug    ranking, utility, and abstention explanation
memcoder utility-summary    intervention outcome calibration
memcoder project-resurrect  bounded project continuation brief
memcoder project-handoff    privacy-safe cognition capsule
memcoder storage status     durable record and audit counts
memcoder storage upgrade    dry-run, back up, apply, and validate the additive schema
memcoder service serve      localhost adapter service
memcoder studio             browser Studio
```

Run `memcoder <command> --help` for exact input requirements.

## Evidence without hype

MemCoder has one narrow controlled transfer result: three baseline AGY runs
passed the visible test but failed private robustness checks; six
MemCoder-assisted runs passed those same private checks. That supports one
claim—in that setup, a verified validation procedure transferred to unseen
variants.

It does **not** establish universal improvement across models, repositories, or
tasks. Provider independence, retrieval safety, QA admission, lifecycle
idempotence, host parity, Dreaming, branch proof gates, and outcome closure have
deterministic coverage. Broad real-project improvement, median token savings,
and production-scale latency remain evaluation targets.

- [Controlled transfer result](docs/beta2_controlled_transfer_results.md)
- [Evaluation protocol](docs/beta2_evaluation_protocol.md)
- [Real-project evaluation protocol](docs/beta2_real_project_evaluation.md)

Current non-goals:

- no claim of consciousness or human-equivalent cognition;
- no silent self-modification of trusted memory;
- no required cloud account or hosted model in Core;
- no team or multi-agent memory in Beta 3.5; and
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
python tests/test_beta34_reliability.py
python tests/test_beta35_release.py
python tests/test_mcp_provider_independence.py
python tests/test_qa_admission.py
python tests/test_retrieval_safety.py
```

These checks have no model-provider requirement.

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

[MIT](LICENSE) © [Shikhar-code](https://github.com/Shikhar-code)
