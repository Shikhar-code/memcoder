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

### Install the plugin

From the activated environment and repository folder used above, run:

```bash
python scripts/configure_agy_plugin.py
agy plugin install .
agy plugin enable memcoder
```

Restart AGY, then check its MCP Servers view. You should see:

- `memcoder_prepare`
- `memcoder_record`

That is the complete one-time setup. The helper writes a local ignored config
with the correct Python path, so no JSON editing is required.

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
