"""
File manager — open, save, and track the current file.

Fires events from core.event_bus; does not touch the UI directly.
"""

import os
from pathlib import Path

from neo_code.core import event_bus


class FileManager:
    def __init__(self) -> None:
        self.current_path: Path | None = None

    # ── Public API ────────────────────────────────────────────────────────────

    def new_file(self) -> None:
        self.current_path = None
        event_bus.publish(event_bus.FILE_NEW)

    def open_file(self, path: str | Path) -> str:
        path = Path(path)
        content = path.read_text(encoding="utf-8")
        self.current_path = path
        event_bus.publish(event_bus.FILE_OPENED, path=str(path), content=content)
        return content

    def save_file(self, content: str, path: str | Path | None = None) -> Path:
        target = Path(path) if path else self.current_path
        if target is None:
            raise ValueError("No file path provided and no file is currently open.")
        target.write_text(content, encoding="utf-8")
        self.current_path = target
        event_bus.publish(event_bus.FILE_SAVED, path=str(target))
        return target

    def save_file_as(self, content: str, path: str | Path) -> Path:
        return self.save_file(content, path)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def current_filename(self) -> str:
        return self.current_path.name if self.current_path else "Untitled"

    @property
    def has_file(self) -> bool:
        return self.current_path is not None
