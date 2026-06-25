import json
from pathlib import Path


def save_domain(domain, memories):

    base_path = Path(__file__).parent.parent

    path = base_path / "data" / domain / "experiences.json"

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            memories,
            f,
            indent=4
        )