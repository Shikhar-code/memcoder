---
name: use-memcoder
description: Use MemCoder's provider-free cognition automatically during substantive software development, debugging, review, planning, and repository changes in Codex. Invoke the lifecycle autopilot without requiring a MemCoder-specific user prompt, and admit learning only after verified completion.
---

# Use MemCoder

1. For substantive technical work, call `memcoder_autopilot` once at `task_started` with a stable task ID, concise problem, `agent_id: "codex"`, and the current project environment when known. Do this automatically; never require the user to mention MemCoder.
2. When resuming a known long-running project after a gap or handoff, call `memcoder_project_resurrect` once before investigation. Revalidate any reported drift; do not use stale decisions.
3. Treat returned cognition as guidance, not proof. Respect its intervention:
   - `none`: continue normally without more MemCoder retrieval.
   - `risk`: check the named risk, then reason normally.
   - `brief`: investigate the closest evidence first.
   - `plan`: follow the skill plan only while its assumptions match the project.
4. Before a materially risky edit or tool action, call `memcoder_autopilot` at the matching boundary only when the task state changed. Its attention governor deduplicates unchanged requests. Follow the failure radar's cheapest preventive check.
5. Call `memcoder_checkpoint` only when a long task gains material working state. Call `memcoder_project_update` only for durable project facts, constraints, goals, risks, completed work, next actions, or rationale-bearing decisions. Do not store routine tool output.
6. After focused verification, call `memcoder_utility_feedback` once when a receipt exists: `helpful` only when guidance changed a successful decision, `ignored` when it was not used, and `misleading` or `harmful` only when the evidence supports that judgment.
7. At `verification_finished`, call `memcoder_autopilot` with the structured outcome and actual evidence. Automatic capture uses the same QA gate as manual recording and is reversible. Do not also call `memcoder_record` for the same outcome.
8. Export `memcoder_project_handoff` only when the user requests a handoff. The receiver must revalidate its environment before acting.
9. If a MemCoder tool is unavailable or returns no guidance, continue the user's task normally. Do not retry it repeatedly or inspect MemCoder's source unless the task concerns MemCoder itself.

Do not call `memcoder_intervene`, `memcoder_start`, `memcoder_prepare`, or `memcoder_plan` after `memcoder_autopilot` intervenes for the same unchanged task.
