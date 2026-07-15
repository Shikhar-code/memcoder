from pathlib import Path
import os
import chromadb

base_path = Path(__file__).parent.parent

db_path = Path(
    os.environ.get(
        "MEMCODER_DB_PATH",
        str(base_path / "chroma_db")
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
