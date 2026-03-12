"""
Terminal panel — read-only output console.

Connects to:
  event_bus.stdout_received  — appends plain text
  event_bus.stderr_received  — appends text in red
  event_bus.execution_started — clears the terminal
"""

from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QColor, QTextCursor, QTextCharFormat, QFont
from PyQt6.QtCore import pyqtSlot

from neo_code.core.event_bus import event_bus


class TerminalPanel(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self._fmt_stdout = self._make_fmt("#E0E0E0")
        self._fmt_stderr = self._make_fmt("#FF6B6B")

        self.setReadOnly(True)
        self.setMaximumBlockCount(2000)  # cap memory on low-RAM device
        font = QFont("Monospace", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: none;
            }
        """)

        self._connect_signals()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _make_fmt(color: str) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        return fmt

    # ── Signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        event_bus.execution_started.connect(self.clear)
        event_bus.stdout_received.connect(self._on_stdout)
        event_bus.stderr_received.connect(self._on_stderr)

    # ── Handlers ──────────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_stdout(self, text: str) -> None:
        self._append(text, self._fmt_stdout)

    @pyqtSlot(str)
    def _on_stderr(self, text: str) -> None:
        self._append(text, self._fmt_stderr)

    def _append(self, text: str, fmt: QTextCharFormat) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text + "\n", fmt)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
