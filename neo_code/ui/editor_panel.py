"""
Editor panel — QPlainTextEdit with Python syntax highlighting.

Emits:
  event_bus.code_changed (code: str)  — debounced 300 ms after last keystroke

Connects to:
  event_bus.file_opened  — loads content into editor
  event_bus.file_new     — clears editor
  event_bus.project_opened — loads project starter code
"""

import keyword
import re

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextDocument
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot

from neo_code.core.event_bus import event_bus
from neo_code.core.settings import Settings


# ── Syntax Highlighter ────────────────────────────────────────────────────────

class PythonHighlighter(QSyntaxHighlighter):
    """Lightweight Python syntax highlighter."""

    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self._rules: list[tuple[re.Pattern, QTextCharFormat]] = []
        self._build_rules()

    def _fmt(self, color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def _build_rules(self) -> None:
        kw_fmt = self._fmt("#C792EA", bold=True)
        for kw in keyword.kwlist:
            self._rules.append((re.compile(rf"\b{kw}\b"), kw_fmt))

        builtin_fmt = self._fmt("#82AAFF")
        builtins = ["print", "len", "range", "int", "str", "float", "list",
                    "dict", "set", "tuple", "bool", "type", "input", "open",
                    "enumerate", "zip", "map", "filter", "sorted", "abs", "round"]
        for b in builtins:
            self._rules.append((re.compile(rf"\b{b}\b"), builtin_fmt))

        # Strings (single and double quoted, non-greedy)
        str_fmt = self._fmt("#C3E88D")
        self._rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), str_fmt))
        self._rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), str_fmt))

        # Numbers
        self._rules.append((re.compile(r"\b\d+(\.\d+)?\b"), self._fmt("#F78C6C")))

        # Decorators
        self._rules.append((re.compile(r"@\w+"), self._fmt("#FFCB6B")))

        # Comments — must be last (overrides everything after #)
        self._comment_fmt = self._fmt("#546E7A", italic=True)

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)

        # Inline comment: find first # not inside a string
        in_str, str_char = False, ""
        for i, ch in enumerate(text):
            if in_str:
                if ch == str_char:
                    in_str = False
            elif ch in ('"', "'"):
                in_str, str_char = True, ch
            elif ch == "#":
                self.setFormat(i, len(text) - i, self._comment_fmt)
                break


# ── Editor Widget ─────────────────────────────────────────────────────────────

class EditorPanel(QPlainTextEdit):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings
        self._highlighter = PythonHighlighter(self.document())
        self._change_timer = QTimer(self)
        self._change_timer.setSingleShot(True)
        self._change_timer.setInterval(300)

        self._apply_style()
        self._connect_signals()

    # ── Style ─────────────────────────────────────────────────────────────────

    def _apply_style(self) -> None:
        font = QFont("Monospace", self._settings.font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(
            self.fontMetrics().horizontalAdvance(" ") * self._settings.tab_width
        )
        self.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.WidgetWidth
            if self._settings.word_wrap
            else QPlainTextEdit.LineWrapMode.NoWrap
        )
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E2E;
                color: #CDD6F4;
                border: none;
                selection-background-color: #45475A;
            }
        """)

    # ── Signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self.textChanged.connect(self._on_text_changed)
        self._change_timer.timeout.connect(self._emit_code_changed)
        event_bus.file_opened.connect(self._on_file_opened)
        event_bus.file_new.connect(self._on_file_new)
        event_bus.project_opened.connect(self._on_project_opened)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_code(self) -> str:
        return self.toPlainText()

    def set_code(self, content: str) -> None:
        self.blockSignals(True)
        self.setPlainText(content)
        self.blockSignals(False)

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_text_changed(self) -> None:
        self._change_timer.start()

    def _emit_code_changed(self) -> None:
        event_bus.code_changed.emit(self.get_code())

    @pyqtSlot(str, str)
    def _on_file_opened(self, _path: str, content: str) -> None:
        self.set_code(content)

    @pyqtSlot()
    def _on_file_new(self) -> None:
        self.set_code("")

    @pyqtSlot(object)
    def _on_project_opened(self, project) -> None:
        if hasattr(project, "starter_code"):
            self.set_code(project.starter_code)
