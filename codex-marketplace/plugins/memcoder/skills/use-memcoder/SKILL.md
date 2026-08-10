---
name: use-memcoder
description: Use MemCoder's provider-free cognition during software development, debugging, review, planning, and repository changes in Codex. Invoke implicitly for substantive technical work when the MemCoder MCP tools are available, especially before investigation or edits and after verified completion.
---

# Use MemCoder

1. When resuming a known long-running project after a gap or handoff, call `memcoder_project_resurrect` once before investigation. Revalidate any reported drift; do not use stale decisions.
2. Before substantive investigation or edits, call `memcoder_intervene` exactly once with a concise problem statement, `agent_id: "codex"`, and the current project environment when known.
3. Treat the returned packet and receipt as guidance, not proof. Respect its intervention:
   - `none`: continue normally without more MemCoder retrieval.
   - `risk`: check the named risk, then reason normally.
   - `brief`: investigate the closest evidence first.
   - `plan`: follow the skill plan only while its assumptions match the project.
4. Before editing, perform the packet's reuse check against the current project and available native behavior. Keep verified facts separate from hypotheses, then test the prediction using the required verification.
5. Call `memcoder_checkpoint` only when a long task gains material working state. Call `memcoder_project_update` only for durable project facts, constraints, goals, risks, completed work, next actions, or rationale-bearing decisions. Do not store routine tool output.
6. After focused verification, call `memcoder_utility_feedback` once when a receipt exists: `helpful` only when guidance changed a successful decision, `ignored` when it was not used, and `misleading` or `harmful` only when the evidence supports that judgment.
7. After focused verification passes, call `memcoder_record` once with the changed files, concise cause and solution, and the actual verification command and output. Never record a failed or unverified result.
8. Export `memcoder_project_handoff` only when the user requests a handoff. The receiver must revalidate its environment before acting.
9. If a MemCoder tool is unavailable or returns no guidance, continue the user's task normally. Do not retry it repeatedly or inspect MemCoder's source unless the task concerns MemCoder itself.

Do not call `memcoder_start`, `memcoder_prepare`, or `memcoder_plan` after `memcoder_intervene` for the same task.
