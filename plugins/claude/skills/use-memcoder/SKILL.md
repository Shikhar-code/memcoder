---
name: use-memcoder
description: Use MemCoder automatically for substantive development work.
---

# MemCoder lifecycle

For substantive development tasks, use the configured MemCoder MCP server:

1. Send `memcoder_autopilot` with `event: task_started` before investigation.
2. Treat returned guidance as a hypothesis, never as proof.
3. Use `memcoder_project_resurrect` when resuming known project work.
4. Surface applicable Failure Frontiers before risky edits.
5. Verify the host's work normally.
6. Send `memcoder_autopilot` with `event: verification_finished` and the actual
   host evidence only after verification passes.
7. Include `guidance_used`, `changed_action`, and `verification_passed` when
   available, plus compact evidence, rework count, and host token usage.
8. Do not record failed or unverified outcomes.

MemCoder is provider-free and fail-open. If its server is unavailable, continue
the task normally and report the missing cognition only when useful.
