# MemCoder Beta-1 release scope

Version: `0.1.0b1`

## Supported claim

MemCoder Beta-1 is a provider-independent persistent cognition layer for
MCP-capable agents. The host agent performs reasoning; MemCoder retrieves
trusted guidance before a task and stores validated structured outcomes after a
successful task.

The supported MCP tools are:

- `memcoder_prepare(problem, agent_id, include_shared)`
- `memcoder_record(task, files, summary, solution, reflection, principles, agent_id)`

The base package does not require Ollama. Legacy `solve()` and `learn()` remain
available only through the `memcoder[ollama]` optional extra.

## Beta-1 validation completed

- Low-confidence and weak lexical matches are filtered before guidance is
  returned.
- Low-quality experiences and non-process reflections are rejected at
  admission, with rejection feedback returned from `memcoder_record`.
- Antigravity completed a two-task owner-isolated transfer proof: the second
  task retrieved the first task's experience and passed an unseen regression.
- A matched no-memory control passed its public test but failed that unseen
  regression.
- A clean installed package, without Ollama, imported the MCP server, recorded
  an outcome, and retrieved it in a fresh Antigravity conversation.

## Explicit non-goals

- MemCoder does not call or bundle a reasoning model in the base package.
- MemCoder does not assess rendered video, images, or visual quality.
- Planning, skills, distributed synchronization, and advanced multi-agent
  policy are not Beta-1 commitments.

## Release action remaining

Publish this version to PyPI. Until publication, `pip install memcoder` may
resolve the earlier `0.1.0a0` package rather than this Beta-1 build.
