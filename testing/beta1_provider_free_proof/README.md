# Provider-free Beta-1 proof fixture

Use agent id `antigravity-provider-free-proof-v2` and pass
`include_shared=false` to every `memcoder_prepare` call. That produces an
empty, owner-only baseline and keeps the proof independent from earlier shared
Antigravity memories.

1. Ask Antigravity to solve `service_config.py` first. It must call
   `memcoder_prepare`, make the smallest fix, pass
   `python testing/beta1_provider_free_proof/test_service_config.py`, then call
   `memcoder_record`.
2. In a fresh Antigravity conversation, ask it to solve `deployment_config.py`
   with the same agent id. Its `memcoder_prepare` result should retrieve the
   first validation experience and use `memory_guided` strategy before it edits
   anything. It must then pass
   `python testing/beta1_provider_free_proof/test_deployment_config.py` and
   record the actual successful outcome.
3. Verify stored evidence:

   ```powershell
   python scripts/verify_beta1_proof.py `
     --owner antigravity-provider-free-proof-v2 `
     --query "deployment configuration is missing its required deployment name" `
     --exclude-shared `
     --min-experiences 2 `
     --min-reflections 1
   ```

The fixture is intentionally small. It tests the cognition loop, not an
agent's ability to discover a complex fix.
