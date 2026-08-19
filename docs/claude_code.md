# Claude Code integration (provider-free)

Claude Code can connect to MemCoder through its supported MCP configuration
surface. From the project root, use the Python environment where MemCoder is
installed:

```powershell
python -m pip install --no-build-isolation .
python -m memcoder setup-claude
python -m memcoder doctor --host claude
```

The setup command writes or updates `.mcp.json`, preserves other MCP servers,
backs up an existing file when it changes, and adds an idempotent MemCoder
section to `CLAUDE.md`. Restart Claude Code after setup.

For a portable repository bundle, see `plugins/claude/`. It contains the
MemCoder skill and an MCP configuration example. Claude Code remains the model
host; MemCoder is local, provider-free, fail-open, and evidence-gated.

For substantive tasks, the skill uses this lifecycle:

```text
task_started → guidance or abstention → host verification → evidence-gated capture
```

At `verification_finished`, Claude should include `guidance_used`,
`changed_action`, and `verification_passed` when known, plus compact evidence,
rework count, and host token usage. This closes the prediction receipt and
calibrates future retrieval only from host-supplied proof.

Use `python -m memcoder host-manifest --host claude` to inspect the contract.
