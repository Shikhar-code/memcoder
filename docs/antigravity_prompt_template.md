# Antigravity prompt template

Copy this at the start of an AGY task and replace the bracketed values.

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

Use a distinct stable `agent_id` for every project. Keep
`include_shared: false` for early testing, then enable shared memory only when
you intentionally want cross-project knowledge.
