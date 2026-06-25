import json
from pathlib import Path


def load_raw(domain):

    base_path = Path(__file__).parent.parent

    path = base_path / "data" / domain / "raw.txt"

    with open(path, "r", encoding="utf-8") as f:

        return json.load(f)