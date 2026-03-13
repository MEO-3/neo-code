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

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout
from PyQt5.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
    QTextDocument, QPainter, QPaintEvent, QResizeEvent,
)
from PyQt5.QtCore import Qt, QTimer, QRect, QSize, pyqtSlot

from neo_code.core.event_bus import event_bus
from neo_code.core.settings import Settings
from neo_code.theme.colors import colors


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
            fmt.setFontWeight(QFont.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def _build_rules(self) -> None:
        kw_fmt = self._fmt(colors.syn_keyword, bold=True)
        for kw in keyword.kwlist:
            self._rules.append((re.compile(rf"\b{kw}\b"), kw_fmt))

        builtin_fmt = self._fmt(colors.syn_builtin)
        builtins = ["print", "len", "range", "int", "str", "float", "list",
                    "dict", "set", "tuple", "bool", "type", "input", "open",
                    "enumerate", "zip", "map", "filter", "sorted", "abs", "round"]
        for b in builtins:
            self._rules.append((re.compile(rf"\b{b}\b"), builtin_fmt))

        str_fmt = self._fmt(colors.syn_string)
        self._rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), str_fmt))
        self._rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), str_fmt))

        self._rules.append((re.compile(r"\b\d+(\.\d+)?\b"), self._fmt(colors.syn_number)))
        self._rules.append((re.compile(r"@\w+"), self._fmt(colors.syn_decorator)))
        self._comment_fmt = self._fmt(colors.syn_comment, italic=True)

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


# ── Line Number Area ──────────────────────────────────────────────────────────

class _LineNumberArea(QWidget):
    """Painted gutter that shows line numbers beside the editor."""

    def __init__(self, editor: "EditorPanel") -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self._editor.paint_line_numbers(event)


# ── Editor Widget ─────────────────────────────────────────────────────────────

class EditorPanel(QPlainTextEdit):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings
        self._highlighter = PythonHighlighter(self.document())
        self._change_timer = QTimer(self)
        self._change_timer.setSingleShot(True)
        self._change_timer.setInterval(300)

        self._line_number_area = _LineNumberArea(self)

        self._apply_style()
        self._connect_signals()
        self._update_line_number_width(0)

    # ── Style ─────────────────────────────────────────────────────────────────

    def _apply_style(self) -> None:
        font = QFont("Monospace", self._settings.font_size)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setTabStopDistance(
            self.fontMetrics().horizontalAdvance(" ") * self._settings.tab_width
        )
        self.setLineWrapMode(
            QPlainTextEdit.WidgetWidth
            if self._settings.word_wrap
            else QPlainTextEdit.NoWrap
        )
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {colors.editor_bg};
                color: {colors.editor_text};
                border: none;
                selection-background-color: {colors.editor_selection};
            }}
        """)

    # ── Line numbers ──────────────────────────────────────────────────────────

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        return 14 + self.fontMetrics().horizontalAdvance("9") * max(digits, 3)

    def _update_line_number_width(self, _block_count: int = 0) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, rect.y(), self._line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_width()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def paint_line_numbers(self, event: QPaintEvent) -> None:
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor(colors.surface))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        line_height = self.fontMetrics().height()

        painter.setFont(self.font())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(colors.text_secondary))
                painter.drawText(
                    0, top,
                    self._line_number_area.width() - 6,
                    line_height,
                    Qt.AlignRight,
                    str(block_number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    # ── Signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self.blockCountChanged.connect(self._update_line_number_width)
        self.updateRequest.connect(self._update_line_number_area)
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
