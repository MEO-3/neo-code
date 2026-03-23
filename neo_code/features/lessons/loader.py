import json
from pathlib import Path


def load_lesson_pack() -> dict:
    path = Path(__file__).parent / "data" / "lesson_pack.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
