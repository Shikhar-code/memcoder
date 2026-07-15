# MemCoder

> Persistent, provider-independent cognition for AI coding agents.

MemCoder gives an agent durable memory without owning its model. Before a task,
the agent retrieves trusted experiences, principles, mistakes, and debugging
reflections. After a verified result, it records a structured outcome for use
on related future work.

Beta-1 is proven with Antigravity CLI over MCP. It does **not** require Ollama,
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
- Provides structured Python SDK access through `prepare()` and `record()`.
- Has a controlled Antigravity proof where memory-guided work passed an unseen
  regression that a matched no-memory control failed.

MemCoder does not generate answers or judge rendered image/video quality. The
host agent supplies reasoning; MemCoder supplies cognition and persistence.

## Installation

### Install from this repository (recommended for Beta-1 testers)

Requirements: Python 3.10+ and internet access the first time Python packages
and the embedding model are installed.

Windows PowerShell:

```powershell
git clone https://github.com/<your-account>/memcoder.git
cd memcoder
python -m venv memcoder-env
.\memcoder-env\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
```

macOS/Linux:

```bash
git clone https://github.com/<your-account>/memcoder.git
cd memcoder
python3 -m venv memcoder-env
source memcoder-env/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

Verify the installed MCP server and confirm Ollama is absent:

```bash
python -c "from adapters.mcp.server import mcp; print('PASS: MemCoder MCP imports')"
python -m pip show ollama
```

The second command should report that `ollama` is not installed. Until this
Beta-1 build is published to PyPI, use `python -m pip install .` rather than
`pip install memcoder`.

### Optional legacy Ollama helpers

The old `solve()` and `learn()` helpers are not part of the Beta-1 MCP workflow.
Install them only if you intentionally want that legacy path:

```bash
python -m pip install "memcoder[ollama]"
```

## Use with Antigravity CLI (AGY)

### Global MCP configuration

1. Install MemCoder in a virtual environment as above.
2. Find that environment's Python executable:
   - Windows: `<project>\memcoder-env\Scripts\python.exe`
   - macOS/Linux: `<project>/memcoder-env/bin/python`
3. Open AGY's global MCP configuration:
   - Windows: `C:\Users\<you>\.gemini\config\mcp_config.json`
   - macOS/Linux: `~/.gemini/config/mcp_config.json`
4. Add or replace the `memcoder` entry, using your actual Python path.

```json
{
  "mcpServers": {
    "memcoder": {
      "command": "C:\\absolute\\path\\to\\memcoder-env\\Scripts\\python.exe",
      "args": ["-m", "adapters.mcp.server"]
    }
  }
}
```

5. Fully restart Antigravity.
6. Confirm its MCP Servers view exposes `memcoder_prepare` and
   `memcoder_record`.

Do not set `cwd` to the MemCoder repository for an installed-package test. It
could make AGY import the checkout rather than the installed package.

### Plugin installation

This repository includes [plugin.json](plugin.json) and a portable
[mcp_config.example.json](mcp_config.example.json).

1. Create `~/.gemini/config/plugins/memcoder/`.
2. Copy `plugin.json` into that folder.
3. Copy `mcp_config.example.json` there, rename it `mcp_config.json`, and
   replace `<absolute-python-path>` with the installed environment's Python.
4. Restart Antigravity and confirm the MemCoder plugin in its MCP Servers view.

The template deliberately has no hard-coded local path.

### Required AGY prompt template

AGY may otherwise inspect MemCoder files or skip the tools. Start each task
with this template, replacing bracketed values:

```text
Use MemCoder's provider-free cognition workflow for this task.

Before inspecting, listing, reading, searching, or editing project files, call
memcoder_prepare exactly once with:
- problem: "[describe the task and expected result]"
- agent_id: "[stable project-specific owner]"
- include_shared: false

Use returned memories as investigation guidance, never as proof. Do not inspect
or edit MemCoder's source code, database, MCP configuration, tool manifests,
or documentation unless the user explicitly asks to debug MemCoder itself.

Solve only the requested project task. Make the smallest correct change and run
the relevant test, render, or verification command.

Only after verification passes, call memcoder_record once with the actual task,
changed files, root-cause summary, solution, one genuine debugging-process
reflection, and reusable principles. Do not record an outcome if verification
failed.

Finally report the MemCoder prepare result, files changed, verification result,
and record result.
```

Use a stable `agent_id` per project. Start with `include_shared: false` to
avoid importing another project's shared memories. See the standalone
[AGY prompt template](docs/antigravity_prompt_template.md).

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
