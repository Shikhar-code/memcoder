import importlib
import sys
import types
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)


for name in [
        "agent.solve_and_learn",
        "agent.problem_solver",
        "memory.conversation_learner"]:
    sys.modules.pop(name, None)


calls = {}

solver = types.ModuleType("agent.problem_solver")


def solve_problem(*args, **kwargs):
    calls["solve"] = {
        "args": args,
        "kwargs": kwargs
    }

    return {
        "answer": "Validate the request before processing it."
    }


solver.solve_problem = solve_problem
sys.modules["agent.problem_solver"] = solver

learner = types.ModuleType("memory.conversation_learner")


def learn_from_conversation(*args, **kwargs):
    calls["learn"] = {
        "args": args,
        "kwargs": kwargs
    }

    return {
        "experience": {
            "task": "Validate incoming API payload"
        }
    }


learner.learn_from_conversation = learn_from_conversation
sys.modules["memory.conversation_learner"] = learner

module = importlib.import_module("agent.solve_and_learn")

result = module.solve_and_learn(
    "The API accepts an invalid payload.",
    session_context="The endpoint processes JSON.",
    agent_id="antigravity"
)

assert calls["solve"]["kwargs"]["agent_id"] == "antigravity"
assert calls["solve"]["kwargs"]["session_context"] == (
    "The endpoint processes JSON."
)
assert calls["learn"]["kwargs"]["agent_id"] == "antigravity"
assert "MemCoder answer:" in calls["learn"]["args"][0]
assert result["learned_memory"]["experience"]["task"] == (
    "Validate incoming API payload"
)

print("PASS: autonomous learning contract")
