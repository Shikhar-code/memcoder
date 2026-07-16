# MemCoder

> Persistent, provider-independent cognition for AI coding agents.

MemCoder gives an agent durable memory without owning its model. Before a task,
the agent retrieves trusted experiences, principles, mistakes, and debugging
reflections. After a verified result, it records a structured outcome for use
on related future work.

Beta-1.1 is proven with Antigravity CLI over MCP. It does **not** require Ollama,
CUDA, or a local generation server.

```text
agent task -> memcoder_prepare -> trusted guidance
          -> host agent reasons, edits, and verifies
          -> memcoder_record -> persistent memory
```

## What Beta-1 does

- Stores persistent experiences, principles, reflections, and mistakes.
- Retrieves confidence-gated, query-relevant memories.
- Keeps memory private per `agent_id`, with optional shared-memory retrieval.
- Exposes provider-free MCP tools for agent hosts.
- Rejects low-quality records and explains rejected fields.
- Bootstraps project guidance from approved Markdown instruction files.
- Provides structured Python SDK access through `prepare()` and `record()`.
- Has a controlled Antigravity proof where memory-guided work passed an unseen
  regression that a matched no-memory control failed.

MemCoder does not generate answers or judge rendered image/video quality. The
host agent supplies reasoning; MemCoder supplies cognition and persistence.

## Installation

### One-command AGY setup (recommended)

Requirements: Python 3.10+, internet access the first time Python packages and
the embedding model are installed, and AGY already installed.

Windows PowerShell:

```powershell
py -m pip install --upgrade pip setuptools wheel; py -m pip install --no-build-isolation "https://github.com/Shikhar-code/memcoder/archive/refs/heads/main.zip"; py -m memcoder setup-agy
```

macOS/Linux:

```bash
python3 -m pip install --upgrade pip setuptools wheel && python3 -m pip install --no-build-isolation "https://github.com/Shikhar-code/memcoder/archive/refs/heads/main.zip" && python3 -m memcoder setup-agy
```

This installs MemCoder and its requirements, then configures AGY with the exact
Python that installed it. The first install can take a few minutes while Python
downloads packages and the embedding model. Restart AGY when it finishes; no
plugin-install command or manual JSON editing is required.

### Install from a local checkout

For contributors or offline local testing:

```powershell
python -m pip install --no-build-isolation .
python -m memcoder setup-agy
```

Verify the installed MCP server and confirm Ollama is absent:

```bash
python -c "from adapters.mcp.server import mcp; print('PASS: MemCoder MCP imports')"
python -m pip show ollama
```

The second command should report that `ollama` is not installed. Until MemCoder
is published to PyPI, the one-command setup installs the current GitHub `main`
branch.

### Optional legacy Ollama helpers

The old `solve()` and `learn()` helpers are not part of the Beta-1 MCP workflow.
Install them only if you intentionally want that legacy path:

```bash
python -m pip install "memcoder[ollama]"
```

## Use with Antigravity CLI (AGY)

### Configure AGY manually (advanced)

The one-command installer above is preferred. If you need to configure an
already-installed local checkout manually, run:

```bash
python -m memcoder setup-agy
```

Restart AGY, then check its MCP Servers view. You should see:

- `memcoder_prepare`
- `memcoder_record`

That is the complete one-time setup. It safely preserves other AGY MCP servers
and updates only the `memcoder` entry.

### First task with MemCoder

Paste this into AGY for the first task in a project:

```text
Use MemCoder for this task.

Before working, call memcoder_prepare once for the task. Then solve the task,
make the smallest correct change, and run the relevant test or render.

If verification passes, call memcoder_record once with what changed, why it
failed, and how it was fixed. Do not record anything if verification failed.

Do not inspect MemCoder's own files unless I specifically ask you to debug
MemCoder.
```

On a first run, `memcoder_prepare` normally returns no memories. That is
expected: the successful outcome you record becomes useful on related later
tasks.

### Later tasks in the same project

Use this shorter prompt:

```text
Use MemCoder for this task: call memcoder_prepare before working, use relevant
memories as guidance, verify the fix, then call memcoder_record if it passes.
Do not inspect MemCoder itself.
```

For most people, that is enough. By default AGY stores memory under the
`antigravity` owner. If you work on multiple unrelated projects, give each one
a simple permanent name such as `remotion-trailer` or `client-dashboard` and
ask AGY to use that name as `agent_id`. An `agent_id` is only a project label;
reuse the same label on every task in that project.

For stricter control or evaluation, use the detailed
[AGY prompt template](docs/antigravity_prompt_template.md).

## What to expect

MemCoder is a persistent cognition layer, not a model or autonomous executor.
Your host agent still reasons, edits, renders, and runs tests; MemCoder supplies
retrieved guidance and records verified outcomes for related future work.

- The first task may retrieve nothing. Value compounds after several verified
  tasks in the same project.
- Use one stable `agent_id` per project so unrelated work does not mix.
- Record outcomes only after the relevant test, build, render, or other
  verification passes. This is the main protection against memory pollution.
- It is strongest for recurring engineering patterns and project conventions.
  It is not a substitute for human judgment on subjective or unverified work.
- Memories are local to the installation and owner by default. Team-wide memory
  sharing and synchronization are outside the Beta-1 scope.

## MCP tools

### `memcoder_prepare`

Retrieves trusted cognition before the host agent works.

```json
{
  "problem": "A deployment configuration rejects a blank required name.",
  "agent_id": "my-project",
  "include_shared": false
}
```

The response includes confidence, strategy (`normal_reasoning`,
`memory_guided`, or `memory_first`), grouped memories, and safe-use
instructions.

### `memcoder_record`

Stores a verified structured outcome after the host agent succeeds.

```json
{
  "task": "Reject blank deployment names before string processing",
  "files": ["src/deployment_validation.py"],
  "summary": "A blank name reached string processing before validation.",
  "solution": "Reject missing or whitespace-only names before processing.",
  "reflection": "I reproduced the blank-input case before changing validation.",
  "principles": ["Validate required values before string operations."],
  "agent_id": "my-project"
}
```

MemCoder returns accepted records and rejected fields. A reflection must be a
short, first-person observation about the debugging process—not a solution.

### `memcoder_import_markdown_file`

Bootstrap a project from Markdown such as `AGENTS.md`, a README, a runbook, or
an architecture guide. MemCoder extracts bullet-point guidance as **candidate
principles**; it does not pretend static documents are experiences or
reflections.

Pass the file path directly—do not paste the document into your prompt. First
request a preview:

```json
{
  "file_path": "AGENTS.md",
  "agent_id": "my-project",
  "approve": false
}
```

Review the returned candidates. To store the same file, call the tool again
with `approve: true`. The path must refer to a UTF-8 `.md` or `.markdown` file
within the project directory where AGY was launched. Imported memories retain
their source filename.

`memcoder_import_markdown` remains available for applications that already have
Markdown content in memory, but most AGY users should use the file tool.

For safety, the importer reads only actionable Markdown bullet points, preserves
wrapped bullet text, skips code blocks, filters common instruction-injection
phrases, and requires explicit approval before writing any memory. Descriptive
README feature lists are shown as rejected rather than stored as principles.

### First run with project instructions

If a project already has `AGENTS.md`, `README.md`, or a runbook, use this AGY
prompt once before normal work:

```text
Call `memcoder_import_markdown_file` once for each of these project instruction
files: [AGENTS.md and any project instruction files]. Use `approve=false`.
Show me the candidate memories. Do not store anything until I approve the
preview. Do not inspect MemCoder's own files.
```

After reviewing the preview, say:

```text
Approve the MemCoder Markdown import you just previewed and store it.
```

## Python SDK example

```python
from memcoder import MemCoderAgent

agent = MemCoderAgent("my-project")

guidance = agent.prepare(
    "A deployment rejects a blank required name.",
    include_shared=False,
)

# Your agent reasons over guidance, edits code, and verifies the result.

agent.record(
    task="Reject blank deployment names before string processing",
    files=["src/deployment_validation.py"],
    summary="Blank names reached string processing before validation.",
    solution="Reject missing or whitespace-only names before processing.",
    reflection="I reproduced the blank-input case before changing validation.",
    principles=["Validate required values before string operations."],
)

project_rules = """
# Project rules
- Run the focused test after every change.
- Keep composition timing explicit.
"""

preview = agent.import_markdown(project_rules, "AGENTS.md")
approved = agent.import_markdown(
    project_rules,
    "AGENTS.md",
    approve=True,
)

# Or import a Markdown file from the current project directory.
preview = agent.import_markdown_file("AGENTS.md")
approved = agent.import_markdown_file("AGENTS.md", approve=True)
```

## Testing

Run the focused Beta-1 checks:

```bash
python tests/test_retrieval_safety.py
python tests/test_retrieval_calibration.py
python tests/test_memory_quality.py
python tests/test_record_quality_feedback.py
python tests/test_mcp_provider_independence.py
python tests/test_shared_retrieval_control.py
python tests/test_ollama_optional.py
```

The complete validated scope and known non-goals are in
[Beta-1 release scope](docs/beta1_release.md).

## Roadmap

Beta-2 work includes planning, skills derived from principles, richer
multi-agent sharing policy, visual-domain evaluation, memory consolidation, and
distributed synchronization.

## License

MIT. See [LICENSE](LICENSE).
