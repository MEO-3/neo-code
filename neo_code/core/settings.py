"""
App settings — JSON-backed, typed accessors.
Stored at ~/.config/neo-code/settings.json
"""

import json
from pathlib import Path

_CONFIG_PATH = Path.home() / ".config" / "neo-code" / "settings.json"

_DEFAULTS: dict = {
    "theme": "dark",
    "font_size": 14,
    "tab_width": 4,
    "word_wrap": False,
    "last_open_dir": str(Path.home()),
}


class Settings:
    def __init__(self) -> None:
        self._data: dict = dict(_DEFAULTS)
        self._load()

    def _load(self) -> None:
        if _CONFIG_PATH.exists():
            try:
                stored = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
                self._data.update(stored)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CONFIG_PATH.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    @property
    def theme(self) -> str:
        return self._data["theme"]

    @theme.setter
    def theme(self, value: str) -> None:
        self._data["theme"] = value

    @property
    def font_size(self) -> int:
        return int(self._data["font_size"])

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._data["font_size"] = value

    @property
    def tab_width(self) -> int:
        return int(self._data["tab_width"])

    @tab_width.setter
    def tab_width(self, value: int) -> None:
        self._data["tab_width"] = value

    @property
    def word_wrap(self) -> bool:
        return bool(self._data["word_wrap"])

    @word_wrap.setter
    def word_wrap(self, value: bool) -> None:
        self._data["word_wrap"] = value

    @property
    def last_open_dir(self) -> str:
        return self._data["last_open_dir"]

    @last_open_dir.setter
    def last_open_dir(self, value: str) -> None:
        self._data["last_open_dir"] = value

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value) -> None:
        self._data[key] = value
