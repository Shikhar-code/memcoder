import ast
import os
from pathlib import Path


source_path = (
    Path(__file__).resolve().parents[1]
    / "memory"
    / "chroma_client.py"
)

source = source_path.read_text(encoding="utf-8")
ast.parse(source, filename=str(source_path))

assert "MEMCODER_DB_PATH" in source
assert "chroma_db" in source

os.environ["MEMCODER_DB_PATH"] = "C:/temporary/memcoder-proof-db"

namespace = {
    "__file__": str(source_path),
    "__name__": "test_chroma_client"
}


class FakeChroma:
    class PersistentClient:
        def __init__(self, path):
            self.path = path


namespace["chromadb"] = FakeChroma

# Replace the import with a stub so the test does not need Chroma installed.
compiled_source = source.replace(
    "import chromadb",
    "chromadb = globals()['chromadb']"
)

exec(
    compile(compiled_source, str(source_path), "exec"),
    namespace
)

assert str(namespace["db_path"]) == "C:\\temporary\\memcoder-proof-db"

print("PASS: database isolation configuration")
