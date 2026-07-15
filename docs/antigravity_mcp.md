# Antigravity MCP setup (provider-free)

Install MemCoder into the Python environment Antigravity uses. For this
unpublished Beta-1 repository, install the checked-out project rather than the
older PyPI package:

```bash
python -m pip install .
```

Then configure Antigravity to start the installed MCP server:

```json
{
  "mcpServers": {
    "memcoder": {
      "command": "<python-with-memcoder-installed>",
      "args": ["-m", "adapters.mcp.server"]
    }
  }
}
```

MemCoder provides two tools:

- `memcoder_prepare(problem, agent_id)` retrieves only trusted memories and
  returns investigation guidance.
- `memcoder_record(task, files, summary, solution, reflection, principles,
  agent_id)` validates and persists the result of a successful fix.

Neither tool invokes an LLM or an Ollama server. Antigravity performs the
reasoning with its own model. A host-agent instruction can therefore enforce
the complete cognition loop without giving the MCP server model-provider
credentials:

```text
For each coding task, call memcoder_prepare exactly once before inspecting or
editing project files. Use only its returned trusted memories as guidance; do
not inspect MemCoder's implementation, database, or configuration files unless
the user explicitly asks to debug MemCoder itself. Solve the assigned project
task normally, make the smallest necessary edit, and run the relevant test.
Only after that test passes, call memcoder_record exactly once with the actual
task, changed files, root-cause summary, implemented solution, one concise
reflection about your debugging process (if justified), and any reusable
principles. Do not record an outcome when the fix or test failed.
```

Use a stable `agent_id` such as `antigravity` for continuity across tasks.

For the current step-by-step installation, plugin setup, and hardened task
prompt, see the [README](../README.md) and
[Antigravity prompt template](antigravity_prompt_template.md).
