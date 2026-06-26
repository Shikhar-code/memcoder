# MemCoder

> **Build AI agents that remember.**

MemCoder is a **persistent semantic memory SDK for AI agents**.

It enables agents to learn from conversations, retrieve relevant past experiences, and build long-term knowledge that improves future reasoning.

Instead of starting from scratch every conversation, agents using MemCoder accumulate knowledge over time.

---

## Why MemCoder?

Large Language Models are powerful, but they typically have no persistent memory between conversations.

MemCoder provides a long-term semantic memory layer that allows agents to:

- Learn from previous conversations
- Remember solved problems
- Reuse past solutions
- Learn from mistakes
- Store reusable principles
- Improve future reasoning

The result is an AI agent that becomes more knowledgeable with experience instead of repeatedly solving the same problems.

---

# Features

- 🧠 Persistent semantic memory
- 🤖 Automatic learning from conversations
- 🔍 Semantic vector search
- 📚 Hierarchical memory retrieval
- 👥 Multi-agent memory isolation
- 🌍 Shared knowledge between agents
- 🔄 Transferable memory ownership
- 💬 Session-based conversations
- ✏️ Memory CRUD operations
- 🧹 Cleanup & maintenance utilities
- ✅ Alpha integration test suite

---

# Installation

Clone the repository

```bash
git clone https://github.com/Shikhar-code/memcoder.git

cd memcoder
```

Install the package

```bash
pip install -e .
```

---

# Quick Start

```python
from memcoder import MemCoderAgent

coder = MemCoderAgent.coder()

conversation = """
User:

torch.cuda.is_available() returns False.

Assistant:

PyTorch was installed without CUDA support.
Install the CUDA-enabled PyTorch build.
"""

coder.learn(conversation)

answer = coder.solve(
    "My GPU is not detected by PyTorch."
)

print(answer["answer"])
```

---

# Examples

The repository includes complete examples demonstrating every major feature.

```
examples/

01_basic.py
02_learning.py
03_sessions.py
04_multi_agent.py
05_crud.py
```

Run an example

```bash
python examples/01_basic.py
```

---

# Core Concepts

## Learning

Convert conversations into structured long-term memories.

```python
coder.learn(conversation)
```

---

## Semantic Search

Retrieve memories using semantic similarity rather than keyword matching.

```python
coder.search("cuda")
```

Retrieve the single most relevant memory.

```python
coder.search_one("cuda")
```

---

## Problem Solving

Use previously stored knowledge during reasoning.

```python
coder.solve(
    "My Docker container exits immediately."
)
```

---

## Sessions

Maintain conversational context across multiple interactions.

```python
session = coder.session()

session.solve(...)

session.solve(...)

session.learn()
```

---

## Multi-Agent Memory

Create independent memory spaces for different agents.

```python
coder = MemCoderAgent.coder()

research = MemCoderAgent.research()

planner = MemCoderAgent.planner()
```

Each agent has private memories while still being able to share knowledge when appropriate.

---

# Memory Types

MemCoder organizes knowledge into four complementary memory types.

### Experience

Previously solved problems and successful solutions.

### Mistake

Common errors and how to avoid them.

### Principle

Reusable knowledge and best practices.

### Reflection

Observations that improve future reasoning.

---

# Memory Management

Update an existing memory

```python
coder.update(memory_id, summary="Updated summary")
```

Delete a memory

```python
coder.delete(memory_id)
```

Share a memory

```python
coder.share(memory_id)
```

Transfer ownership

```python
coder.transfer(memory_id, "research")
```

Clear all memories owned by an agent

```python
coder.clear()
```

---

# Architecture

```text
                  Conversation
                        │
                        ▼
               Learning Pipeline
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   Experiences      Mistakes      Principles
                        │
                        ▼
                  Reflections
                        │
                        ▼
              Semantic Memory Store
                        │
                        ▼
             Hierarchical Retrieval
                        │
                        ▼
                 Agent Reasoning
                        │
                        ▼
                  Better Responses
```

---

# Project Structure

```
memcoder/

agent/
api/
client/
context/
examples/
memory/
scripts/
server/
tests/

README.md
pyproject.toml
requirements.txt
```

---

# Testing

Run the Alpha integration suite.

```bash
python tests/test_alpha.py
```

---

# Maintenance

Repair metadata, remove duplicate memories and clean development artifacts.

```bash
python scripts/cleanup.py
```

---

# Current Status

**Version:** 0.1.0-alpha

Implemented features:

- Persistent semantic memory
- Automatic conversation learning
- Semantic vector search
- Hierarchical retrieval
- Session support
- Multi-agent memory
- Shared knowledge
- Memory ownership transfer
- CRUD operations
- Cleanup utilities
- Integration tests

---

# Roadmap

## Alpha

- Persistent semantic memory
- Learning pipeline
- Hierarchical retrieval
- Multi-agent support
- Session management
- CRUD operations

## Beta

- Memory ranking
- Memory consolidation
- Importance updates
- Forgetting & decay
- Graph relationships
- FastAPI server
- OpenAI integration
- Anthropic integration

## Version 1.0

- Distributed memory backend
- Cloud deployment
- Memory synchronization
- Memory visualization
- Advanced agent collaboration

---

# Contributing

Issues, suggestions and pull requests are welcome.

For significant changes, please open an issue first to discuss the proposed improvement.

---

# License

This project is licensed under the MIT License.

---

## Philosophy

Knowledge should accumulate.

Every solved problem, discovered principle, avoided mistake and useful insight should become part of an agent's long-term memory instead of disappearing at the end of a conversation.

MemCoder is designed to provide that persistent semantic memory layer.

**Build AI agents that remember.**
