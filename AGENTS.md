# Codex instructions

- Make the smallest complete change.
- Do not modify unrelated files.
- Do not redesign the architecture unless explicitly requested.
- Use Serena for symbol navigation and reference lookup.
- Use Context7 only when current third-party documentation is actually needed.
- Reuse existing dependencies and patterns.
- Do not install or update dependencies without asking.
- Run targeted tests before the full test suite.
- Do not run watch-mode or persistent commands.
- Do not repeat the same failed command more than twice.
- Do not use subagents for small tasks.
- Stop and report the blocker after two unsuccessful approaches.
- Keep completion summaries concise.

## Verified setup

```powershell
python -m pip install --no-build-isolation .
python -m memcoder --help
```

## Verified provider-free checks

Run the relevant test first, then these checks for the documented regression pass:

```powershell
python tests/test_automation_cli.py
python tests/test_mcp_provider_independence.py
python tests/test_retrieval_safety.py
python tests/test_memory_quality.py
python tests/test_qa_admission.py
python tests/test_cognition_brief.py
python tests/test_skill_promotion.py
python tests/test_planning.py
python tests/test_skill_health.py
python tests/test_evaluation.py
```

No repository-defined full-suite runner was found.
