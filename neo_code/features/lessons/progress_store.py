import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

_PROGRESS_PATH = Path.home() / ".config" / "neo-code" / "lesson_progress.json"


@dataclass
class LessonProgress:
    attempts: int = 0
    completed: bool = False
    stars: int = 0
    last_attempt: str | None = None


def _load_data() -> dict:
    if _PROGRESS_PATH.exists():
        try:
            return json.loads(_PROGRESS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_data(data: dict) -> None:
    _PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _PROGRESS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_progress(lesson_id: str) -> LessonProgress:
    data = _load_data()
    entry = data.get("lessons", {}).get(lesson_id, {})
    return LessonProgress(
        attempts=int(entry.get("attempts", 0)),
        completed=bool(entry.get("completed", False)),
        stars=int(entry.get("stars", 0)),
        last_attempt=entry.get("last_attempt"),
    )


def record_attempt(lesson_id: str, success: bool) -> LessonProgress:
    data = _load_data()
    lessons = data.setdefault("lessons", {})
    entry = lessons.setdefault(lesson_id, {})

    attempts = int(entry.get("attempts", 0)) + 1
    completed = bool(entry.get("completed", False))
    stars = int(entry.get("stars", 0))

    if success:
        completed = True
        if attempts <= 1:
            new_stars = 3
        elif attempts <= 3:
            new_stars = 2
        else:
            new_stars = 1
        stars = max(stars, new_stars)

    entry.update(
        {
            "attempts": attempts,
            "completed": completed,
            "stars": stars,
            "last_attempt": datetime.now().isoformat(),
        }
    )
    _save_data(data)
    return LessonProgress(
        attempts=attempts,
        completed=completed,
        stars=stars,
        last_attempt=entry["last_attempt"],
    )
