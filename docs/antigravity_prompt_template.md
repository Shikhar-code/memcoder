# Antigravity prompt template

Beta 3.5 setup installs this lifecycle automatically through MCP. Use this
short template only when you need to make the behavior explicit during a
diagnostic or certification run:

```text
Use the configured MemCoder MCP server for this substantive task.

1. Send memcoder_autopilot with host="agy", event="task_started", a stable
   task_id, the task problem, and the current environment.
2. Treat returned guidance as a hypothesis, not proof. Inspect the project and
   solve the requested task normally with the smallest correct edit.
3. Use project resurrection when resuming known work and surface applicable
   Failure Frontiers before risky changes.
4. Run the narrowest relevant verification.
5. Only after successful verification, send memcoder_autopilot with
   event="verification_finished" and the actual host evidence. Include
   guidance_used, changed_action, verification_passed, rework_count, and
   host_tokens when the host can supply them.
6. Do not record a failed or unverified outcome. If MemCoder is unavailable,
   continue normally; the host must remain fail-open.
```

Use a distinct stable `agent_id` for every project. The [AGY MCP setup guide](antigravity_mcp.md)
covers installation and strict host certification.

## Bootstrap existing project guidance

For a project with existing Markdown instructions, ask AGY to call
`memcoder_import_markdown_file` for each relevant file with `approve=false`.
Review the candidate principles, then explicitly ask AGY to call it again with
`approve=true`. The files must be inside the project directory from which AGY
was launched. Do not import a document blindly.
