import importlib
import sys
import types
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)


class FakeCollection:
    def get(self):
        return {
            "ids": ["research-1", "coder-1"],
            "metadatas": [
                {
                    "task": "Validate API payload",
                    "files": ["api.py"],
                    "summary": "A field was missing.",
                    "solution": "Validate required fields.",
                    "importance": 5,
                    "type": "experience",
                    "owner": "research"
                },
                {
                    "task": "Validate API payload",
                    "files": ["api.py"],
                    "summary": "A field was missing.",
                    "solution": "Validate required fields.",
                    "importance": 5,
                    "type": "experience",
                    "owner": "coder"
                }
            ]
        }


chroma = types.ModuleType("memory.chroma_client")
chroma.collection = FakeCollection()
sys.modules["memory.chroma_client"] = chroma

for name in ["memory.consolidator", "memory.find_duplicate_ids"]:
    sys.modules.pop(name, None)

consolidator = importlib.import_module("memory.consolidator")
duplicates = importlib.import_module("memory.find_duplicate_ids")

research_memories = consolidator.find_similar_memories(
    "Validate API payload",
    memory_type="experience",
    owner="research"
)

assert len(research_memories) == 1
assert research_memories[0]["owner"] == "research"
assert duplicates.find_duplicate_ids(
    "Validate API payload",
    memory_type="experience",
    owner="research"
) == ["research-1"]

merged = consolidator.merge_memories(research_memories)
assert merged["owner"] == "research"

print("PASS: multi-agent consolidation isolation")
