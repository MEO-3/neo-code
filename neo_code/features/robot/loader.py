import json
from pathlib import Path


def load_robot_pack() -> dict:
    path = Path(__file__).parent / "data" / "robot_pack.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
