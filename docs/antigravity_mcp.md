# Antigravity MCP setup (provider-free)

Beta 3.5 uses the same automatic lifecycle as Codex and Claude Code and closes
verified intervention outcomes. Install
MemCoder into the Python environment Antigravity will launch, then run:

```powershell
python -m pip install --no-build-isolation .
python -m memcoder setup-agy
python -m memcoder doctor --host agy
```

`setup-agy` updates only the `memcoder` entry in Antigravity's MCP config and
preserves other servers. If the file changes, the previous file is kept beside
it with a `.bak` suffix. Run the command again safely after changing Python
environments.

The host lifecycle is:

```text
task_started
→ optional project_resurrected
→ risk/checkpoint boundaries when needed
→ host work and verification
→ verification_finished or task_failed
→ QA-gated capture, explicit outcome closure, and utility feedback
```

Use `python -m memcoder host-manifest --host agy` to inspect the canonical
contract and `host-certify` with `strict: true` to validate a receipt set.
MemCoder returns guidance, not proof; Antigravity remains responsible for
inspection and verification. If the MCP server is unavailable, Antigravity
continues normally and no outcome is recorded.

At `verification_finished`, include `guidance_used`, `changed_action`, and
`verification_passed` when known, plus compact `evidence`, `rework_count`, and
`host_tokens`. MemCoder uses these fields to close the prediction receipt; it
does not infer helpfulness from a passing task alone.

Neither the Core nor the MCP server invokes an LLM or requires Ollama, CUDA, or
an API key. Antigravity supplies the reasoning model.
