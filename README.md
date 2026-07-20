# MemCoder

> Provider-independent persistent cognition for AI agents and automation.

MemCoder helps an AI agent get better across related tasks without taking over
the agent's model, tools, source code, or application database.

Before work begins, the host retrieves trusted past experiences, mistakes,
reflections, and principles. After the host verifies a successful result, it
stores a structured outcome for relevant future work.

```text
task -> MemCoder prepare -> trusted guidance -> host solves and verifies
     -> MemCoder record -> persistent memory for later related tasks
```

Current version: **Beta-1.2**. It is provider-independent: MemCoder does not
need Ollama, CUDA, or a local generation server.

## Does it work with every AI?

It works with **any AI host or automation system that can call MCP tools or run
a command-line program**. That includes AGY / Antigravity CLI, Gemini- or
Claude-powered scripts, CI jobs, and custom Python applications.

It does not automatically connect to a browser chat window. A host needs one
small workflow integration: call MemCoder before work, give its returned
guidance to the model, verify the result, then record the verified outcome.

| MemCoder owns | Your host still owns |
| --- | --- |
| Durable local memory, retrieval, trust gating, quality checks | Model choice, reasoning, code edits, tests, renders, deployment, project database |

## What Beta-1.2 can do

- Persist four memory types: experiences, mistakes, reflections, and principles.
- Retrieve query-relevant memories with confidence and lexical relevance gates.
- Keep records separated by a simple project label (`agent_id`), with optional
  access to intentionally shared records.
- Reject low-quality experiences, malformed reflections, duplicate records, and
  weak principles, with explicit rejection feedback.
- Work through MCP (best for AGY) or JSON commands (best for any automation).
- Preview and approve actionable guidance from local Markdown instruction files.

It is not yet a generic autonomous planner or skill executor. Those are later
Beta-2 capabilities.

## Installation

### Requirements

- Python 3.10 or newer.
- Internet access on the first install, so Python packages and MemCoder's local
  embedding model can be downloaded.

The first retrieval may take longer than later ones because the embedding model
is initialized locally. MemCoder does not require an API key.

### Install from PyPI

Windows PowerShell:

```powershell
python -m pip install --upgrade memcoder
```

macOS/Linux:

```bash
python3 -m pip install --upgrade memcoder
```

Confirm that the provider-neutral commands are available:

```bash
python -m memcoder --help
```

You should see `setup-agy`, `prepare`, and `record`.

> If Windows says `python` is not recognized, install Python from
> [python.org](https://www.python.org/downloads/) and select **Add Python to
> PATH** during installation. If your system uses `py` instead, replace
> `python` with `py` in the commands above.

### Install a local checkout

For development or local testing from the repository root:

```powershell
python -m pip install --no-build-isolation .
```

## Read-only Markdown knowledge (video branch)

This branch adds a separate **Knowledge** index for large project instruction
corpora. Knowledge is source material - such as subject guides, scene rules,
and rendering constraints - and is never stored as an Experience, Reflection,
Mistake, or learned Principle.

Sync an approved Markdown folder once, or safely run this command at every
automation startup. It indexes only new or changed files and removes chunks for
files deleted from that source folder.

```powershell
python -m memcoder knowledge sync --source "C:\Users\shikh\Knowledge-Base-main"
```

The source remains read-only. MemCoder stores only searchable chunks and their
provenance in its own local `knowledge` collection. A downloaded archive folder
containing one nested knowledge directory is detected automatically.

For each chunk, MemCoder retains the subject folder, production category,
top-level document/scene heading, section heading, source-relative path, and
source hash. It splits long files by document and section before embedding,
which makes a large corpus usable without injecting whole Markdown files into a
model prompt.

To retrieve this knowledge with normal cognition, include the subject and an
optional production category in `prepare.json`:

```json
{
  "problem": "Plan a readable Biology cell-structure explainer scene.",
  "agent_id": "lesson-video-pipeline",
  "include_shared": false,
  "include_knowledge": true,
  "subject": "bio",
  "category": "AI Rendering Rules"
}
```

`memcoder prepare --input prepare.json` returns a separate `knowledge` array
with the source path, headings, content, and relevance confidence. Treat that
array as prerequisite reference context; treat the separate learned-memory
arrays as verified past experience. Set `include_knowledge` to `false` only
when a host deliberately needs a memory-only request.

Check the local index without embedding or changing anything:

```powershell
python -m memcoder knowledge status --source "C:\Users\shikh\Knowledge-Base-main"
```

The report includes indexed chunk count, source-file count, subjects, and
categories. A future automated pipeline should run this health check after its
startup sync and fail clearly if its required knowledge source is absent.

### Project contract for an automated host

Create one local configuration file at the automation project's root. It keeps
the stable memory namespace and the approved Markdown source out of individual
requests:

```powershell
python -m memcoder knowledge configure `
  --source "C:\\path\\to\\Knowledge-Base" `
  --agent-id "lesson-video-pipeline"
```

This writes `.memcoder/knowledge.json`. It is local-only because it contains an
absolute machine path. An automated host can then use the same contract on
every run:

```powershell
python -m memcoder knowledge sync --config .memcoder/knowledge.json
python -m memcoder knowledge status --config .memcoder/knowledge.json
python -m memcoder prepare --config .memcoder/knowledge.json --input prepare.json
```

With `--config`, `prepare.json` needs only the current problem and optional
knowledge scope. The configured `agent_id`, private-memory setting, and
knowledge setting are applied automatically:

```json
{
  "problem": "Plan a readable Biology cell-structure explainer scene.",
  "subject": "bio",
  "category": "AI Rendering Rules"
}
```

## Quick start: any automation host

Use the JSON CLI when your system can run shell commands. It works the same way
whether the underlying model is Gemini, Claude, OpenAI, a local model, or no
model at all.

### 1. Choose a stable project label

`agent_id` is simply a memory namespace. Use one short, stable label per
project, for example `billing-api` or `lesson-video-pipeline`. Reuse the exact
same label on later tasks in that project. This prevents unrelated projects
from mixing memories.

### 2. Retrieve guidance before the host starts work

Create `prepare.json` in your project:

```json
{
  "problem": "Resolve a required-field validation failure and run the focused test.",
  "agent_id": "billing-api",
  "include_shared": false
}
```

Run:

```bash
memcoder prepare --input prepare.json
```

The response includes:

- `confidence`: how strong the closest trusted experience is.
- `strategy`: `normal_reasoning`, `memory_guided`, or `memory_first`.
- typed memories: `experiences`, `mistakes`, `principles`, and `reflections`.

Pass the response to your AI host as **guidance, not proof**. The host should
still inspect the actual project, solve the task, and run its own verification.

### 3. Record only after verification passes

After the host's test, build, render, or other acceptance check passes, create
`record.json`:

```json
{
  "verified": true,
  "task": "Resolved a required-field validation failure.",
  "files": ["src/request_validation.py", "tests/test_request_validation.py"],
  "summary": "The focused test passed after explicit required-field validation was added.",
  "solution": "Validated the required field before processing the request.",
  "reflection": "I reproduced the missing-field case before changing validation.",
  "principles": ["Validate required fields before processing input."],
  "agent_id": "billing-api"
}
```

Run:

```bash
memcoder record --input record.json
```

The CLI requires `"verified": true`. It returns the accepted records plus any
rejected fields. Do not set that flag or record anything when verification
failed; this is the main defense against memory pollution.

### First run versus later runs

On the first task in a project, `prepare` will usually return no memories and
the strategy will be `normal_reasoning`. That is correct. Complete and verify
the task normally, then record it.

On later related tasks using the same `agent_id`, MemCoder can return relevant
past outcomes and switch to `memory_guided` or `memory_first`. Its value grows
from repeated, verified work - not from storing every conversation.

## AGY / Antigravity CLI setup

AGY uses MemCoder through MCP tools. One setup command adds the MemCoder MCP
server to AGY's configuration without changing your other MCP servers.

### One-time setup

1. Install MemCoder using the [Installation](#installation) command above.

2. Run:

   ```bash
   python -m memcoder setup-agy
   ```

3. Fully close and reopen AGY.

4. Start a task. AGY should have these tools available:

   - `memcoder_prepare`
   - `memcoder_record`
   - `memcoder_import_markdown`
   - `memcoder_import_markdown_file`

No Ollama installation, model server, API key, or `agy plugin install` command
is required for this setup.

If AGY cannot see the tools, verify the installed server first:

```bash
python -c "from adapters.mcp.server import mcp; print('MemCoder MCP import OK')"
```

If that reports a missing module, rerun `python -m pip install --upgrade
memcoder` using the same Python environment that you used for `setup-agy`, then
restart AGY.

### First AGY task in a project

Paste this prompt with your actual task below it:

```text
Use MemCoder for this task.

Before inspecting or editing project files, call memcoder_prepare exactly once
with the task description, agent_id: "my-project", and include_shared: false.
Use returned memories only as investigation guidance, never as proof.

Solve only my requested project task. Do not inspect or edit MemCoder's source,
database, configuration, or documentation unless I explicitly ask you to debug
MemCoder itself. Make the smallest correct change and run the relevant test,
build, render, or verification command.

Only if verification passes, call memcoder_record exactly once with the actual
task, changed files, root-cause summary, solution, and any genuine reflection
or reusable principle. Do not record an outcome if verification failed.
```

Replace `my-project` with a permanent project label and reuse it on every task.
The first task normally has no retrieved memories; record the verified result
so the next similar task has useful evidence.

### Later AGY tasks

For subsequent tasks in the same project, this is enough:

```text
Use MemCoder for this task: call memcoder_prepare once before working with
agent_id "my-project" and include_shared false. Use relevant memories as
guidance, verify the result, and call memcoder_record once only if it passes.
Do not inspect MemCoder itself.
```

For a stricter reusable version, see the
[AGY prompt template](docs/antigravity_prompt_template.md).

## MCP tool reference

### `memcoder_prepare`

Call once before work.

```json
{
  "problem": "A deployment configuration rejects a blank required name.",
  "agent_id": "billing-api",
  "include_shared": false
}
```

Set `include_shared` to `false` while establishing a clean project memory. Use
`true` only when you intentionally want records owned by `shared` to be
eligible too.

### `memcoder_record`

Call once after the host has independently verified success.

```json
{
  "task": "Reject blank deployment names before string processing.",
  "files": ["src/deployment_validation.py"],
  "summary": "Blank names reached string processing before validation.",
  "solution": "Reject missing or whitespace-only names before processing.",
  "reflection": "I reproduced the blank-input case before changing validation.",
  "principles": ["Validate required values before string operations."],
  "agent_id": "billing-api"
}
```

MCP has no `verified` field because verification is enforced by the host
workflow and task prompt. The JSON CLI provides an additional hard gate with
`"verified": true`.

## Import existing project instructions from Markdown

Use this when a project has an `AGENTS.md`, runbook, architecture guide, or
other instruction file. MemCoder extracts only actionable bullet-point guidance
as candidate **principles**. It does not treat documents as experiences or
reflections.

From AGY, first preview the file without saving it:

```json
{
  "file_path": "AGENTS.md",
  "agent_id": "billing-api",
  "approve": false
}
```

Review the candidates. Then call the same tool again with `"approve": true`
to store the approved principles.

The Markdown file must be UTF-8, have a `.md` or `.markdown` extension, be
inside the project directory where AGY was launched, and be at most 1 MB.
Code blocks, descriptive feature lists, placeholder text, and common
instruction-injection patterns are rejected rather than stored.

## Local storage and privacy

MemCoder stores memory locally in ChromaDB. By default it uses the package or
checkout's `chroma_db` directory. For an isolated test run, set
`MEMCODER_DB_PATH` to a different local path before calling MemCoder.

Records are scoped by `agent_id`. They are not synchronized to a cloud account
or shared with a team by default.

## Optional legacy Ollama helpers

The old `solve()` and `learn()` helpers are not part of the current Beta-1.2
MCP or JSON CLI workflow. Install their optional dependency only if you
intentionally need that legacy path:

```bash
python -m pip install "memcoder[ollama]"
```

## Verification for contributors

Run the focused provider-free checks from a local checkout:

```bash
python tests/test_automation_cli.py
python tests/test_mcp_provider_independence.py
python tests/test_retrieval_safety.py
python tests/test_retrieval_calibration.py
python tests/test_memory_quality.py
python tests/test_record_quality_feedback.py
python tests/test_ollama_optional.py
```

The validated Beta-1 scope is in [Beta-1 release scope](docs/beta1_release.md).
The implementation architecture is in
[the current architecture PDF](output/pdf/memcoder-current-architecture.pdf).

## Roadmap

Beta-2 will focus on skills derived from proven principles and constrained
planning. See [the roadmap](docs/roadmap.md).

## License

MIT. See [LICENSE](LICENSE).
