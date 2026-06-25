from pathlib import Path
import chromadb

base_path = Path(__file__).parent.parent

db_path = base_path / "chroma_db"

client = chromadb.PersistentClient(
    path=str(db_path)
)

collection = client.get_or_create_collection(
    name="memories"
)