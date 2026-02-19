"""Output panel for displaying program stdout/stderr."""
from __future__ import annotations


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextCharFormat
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton, QHBoxLayout

from neo_code.ui.theme import COLORS


class OutputPanel(QWidget):
    """Panel displaying program execution output (stdout/stderr)."""


    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        title = QLabel("Output")
        title.setObjectName("sectionTitle")
        header.addWidget(title)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setFixedWidth(60)
        self._clear_btn.clicked.connect(self.clear)
        self._clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        header.addWidget(self._clear_btn)
        layout.addLayout(header)

        # Output text area
        self._output = QTextEdit(self)
        self._output.setReadOnly(True)
        self._output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: none;
                padding: 8px;
                font-family: "JetBrains Mono", "Fira Code", monospace;
                font-size: 12px;
            }}
        """)
        layout.addWidget(self._output)

    def append_stdout(self, text: str) -> None:
        """Append stdout text (white)."""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["text_primary"]))
        self._append_formatted(text, fmt)

    def append_stderr(self, text: str) -> None:
        """Append stderr text (red)."""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["error"]))
        self._append_formatted(text, fmt)

    def append_info(self, text: str) -> None:
        """Append info text (blue)."""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["info"]))
        self._append_formatted(text, fmt)

    def _append_formatted(self, text: str, fmt: QTextCharFormat) -> None:
        cursor = self._output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text, fmt)
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()

    def clear(self) -> None:
        """Clear the output."""
        self._output.clear()
