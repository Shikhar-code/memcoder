from pathlib import Path
import os
import sys
import chromadb

base_path = Path(__file__).parent.parent
legacy_workspace_db_path = base_path / "chroma_db"


def default_db_path():
    """Return a writable per-user location without relying on package files."""
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / "MemCoder" / "chroma_db"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "MemCoder" / "chroma_db"
    root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "memcoder" / "chroma_db"

db_path = Path(
    os.environ.get(
        "MEMCODER_DB_PATH",
        str(default_db_path())
    )
)


def set_db_path(path):
    """Switch the active persistent store for a controlled local run."""

    global db_path

    db_path = Path(path)

class ChromaCollectionProxy:
    def _get_col(self):
        client = chromadb.PersistentClient(path=str(db_path))
        return client.get_or_create_collection(name="memories")

    def __getattr__(self, name):
        return getattr(self._get_col(), name)

    def __len__(self):
        return len(self._get_col())

collection = ChromaCollectionProxy()


def legacy_workspace_collection():
    """Return the pre-Beta-2.1 workspace collection when it exists locally."""
    if os.environ.get("MEMCODER_DB_PATH") or legacy_workspace_db_path == db_path:
        return None
    if not legacy_workspace_db_path.exists():
        return None
    client = chromadb.PersistentClient(path=str(legacy_workspace_db_path))
    return client.get_or_create_collection(name="memories")
