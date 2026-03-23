"""
File manager — open, save, and track the current file.

Emits EventBus signals; does not touch the UI directly.
"""

from pathlib import Path

from neo_code.core.event_bus import event_bus


class FileManager:
    def __init__(self) -> None:
        self.current_path: Path | None = None

    # ── Public API ────────────────────────────────────────────────────────────

    def new_file(self) -> None:
        self.current_path = None
        event_bus.file_new.emit()

    def open_file(self, path: str | Path) -> str:
        path = Path(path)
        content = path.read_text(encoding="utf-8")
        self.current_path = path
        event_bus.file_opened.emit(str(path), content)
        return content

    def save_file(self, content: str, path: str | Path | None = None) -> Path:
        target = Path(path) if path else self.current_path
        if target is None:
            raise ValueError("No file path provided and no file is currently open.")
        target.write_text(content, encoding="utf-8")
        self.current_path = target
        event_bus.file_saved.emit(str(target))
        return target

    def save_file_as(self, content: str, path: str | Path) -> Path:
        return self.save_file(content, path)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def current_filename(self) -> str:
        return self.current_path.name if self.current_path else "Chưa đặt tên"

    @property
    def has_file(self) -> bool:
        return self.current_path is not None
