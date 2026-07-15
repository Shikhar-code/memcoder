# Provider-free transfer-ablation proof

This fixture compares a baseline solve with a memory-guided related solve.
Use the owner `antigravity-transfer-ablation-v1` and always set
`include_shared=false` when preparing the second task.

## Stage 1: baseline and seed

Antigravity solves `profile_validation.py` **without calling
`memcoder_prepare`**. It runs only `test_profile_validation.py`, then calls
`memcoder_record` once to seed the successful outcome.
The recorded solution must state that both missing and whitespace-only required
names are rejected before calling `strip()`.

## Stage 2: memory-guided transfer

In a fresh conversation, Antigravity calls `memcoder_prepare` before reading
any project files, then solves `workspace_validation.py` and runs only
`test_workspace_validation.py`. It must not inspect this README or
`verify_workspace_regression.py`.

After it records the successful outcome, run the hold-out check yourself:

```powershell
python testing/beta1_transfer_ablation/verify_workspace_regression.py
```

Passing that unseen related regression is evidence that the memory-guided
solution transferred a detail beyond the public stage-2 test.

## Stage 3: no-memory control

In a new conversation and with a fresh owner, Antigravity solves
`workspace_control_validation.py` without calling `memcoder_prepare` and runs
only `test_workspace_control_validation.py`. Do not let it inspect
`verify_workspace_control_regression.py`. Run that hold-out check afterward
and compare its behavior and result with stage 2.
