# Legacy Beta-1 Antigravity MCP Proof

Date: 2026-07-15

## Scope

This historical proof validated the former Ollama-backed MCP `memcoder_solve`
tool:

```text
solve -> retrieve -> guide -> learn -> persist -> retrieve on a related task
```

The evaluation used the isolated database:

```text
C:\Users\shikh\memcoder\chroma_db_beta1_final_proof
```

## Controlled Tasks

1. `testing/beta1_final_proof/config_validation.py`
   - Missing `environment` must raise `ValueError("environment is required")`.
   - Antigravity used `memcoder_solve` with `proof_trace=true`.
   - Initial trace correctly reported no prior memories and `normal_reasoning`.
   - The fixture test passed.

2. `testing/beta1_final_proof/worker_validation.py`
   - Run in a new Antigravity conversation.
   - Missing `worker_id` must raise `ValueError("worker_id is required")`.
   - Pre-solve trace retrieved the first task's experience, mistake, principle, and reflection.
   - Trace reported confidence `0.73` and strategy `memory_guided`.
   - The fixture test passed.

## Persistence Evidence

After both tasks, the proof database contained:

```text
Owner: antigravity
Experiences: 2
Reflections: 4
Principles: 4
Mistakes: 2
```

The final related-query retrieval reported confidence `0.78`, strategy `memory_guided`, and retrieved the stored `register_worker` experience.

## Conclusion

The controlled evaluation demonstrates the earlier integrated loop, but it does
not demonstrate provider independence: `memcoder_solve` invoked local Ollama.
That tool has been retired from the active MCP surface. The current supported
path is documented in [Antigravity MCP setup](antigravity_mcp.md), using
`memcoder_prepare` and `memcoder_record`. A new proof should be captured with
that provider-free path before declaring Beta-1 complete.
