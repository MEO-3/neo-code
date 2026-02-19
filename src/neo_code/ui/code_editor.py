"""Python code editor widget with syntax highlighting."""
from __future__ import annotations

import re
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, Qt, QRect, QSize
from PyQt6.QtGui import (
    QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextDocument,
    QPainter, QTextFormat,
)
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QTextEdit

from neo_code.ui.theme import EDITOR_COLORS
from neo_code.config.settings import get_settings


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code."""

    KEYWORDS = [
        "and", "as", "assert", "async", "await", "break", "class", "continue",
        "def", "del", "elif", "else", "except", "finally", "for", "from",
        "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
        "or", "pass", "raise", "return", "try", "while", "with", "yield",
        "True", "False", "None",
    ]

    BUILTINS = [
        "print", "range", "len", "int", "float", "str", "list", "dict",
        "tuple", "set", "bool", "input", "type", "isinstance", "enumerate",
        "zip", "map", "filter", "sorted", "reversed", "abs", "max", "min",
        "sum", "round", "open", "super", "property", "staticmethod",
        "classmethod", "hasattr", "getattr", "setattr",
    ]

    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self._rules: list[tuple[re.Pattern, QTextCharFormat]] = []
        self._setup_rules()

    def _make_format(self, color: int, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setProperty(QTextFormat.Property.FontItalic, True)
        return fmt

    def _setup_rules(self) -> None:
        # Keywords
        kw_fmt = self._make_format(EDITOR_COLORS["keyword"], bold=True)
        kw_pattern = r'\b(' + '|'.join(self.KEYWORDS) + r')\b'
        self._rules.append((re.compile(kw_pattern), kw_fmt))

        # Builtins
        bi_fmt = self._make_format(EDITOR_COLORS["builtin"])
        bi_pattern = r'\b(' + '|'.join(self.BUILTINS) + r')\b'
        self._rules.append((re.compile(bi_pattern), bi_fmt))

        # Function/method definitions
        fn_fmt = self._make_format(EDITOR_COLORS["function_name"])
        self._rules.append((re.compile(r'\bdef\s+(\w+)'), fn_fmt))

        # Class definitions
        cls_fmt = self._make_format(EDITOR_COLORS["class_name"], bold=True)
        self._rules.append((re.compile(r'\bclass\s+(\w+)'), cls_fmt))

        # Decorators
        dec_fmt = self._make_format(EDITOR_COLORS["decorator"])
        self._rules.append((re.compile(r'@\w+'), dec_fmt))

        # Numbers
        num_fmt = self._make_format(EDITOR_COLORS["number"])
        self._rules.append((re.compile(r'\b\d+\.?\d*\b'), num_fmt))

        # Strings (single and double quoted)
        str_fmt = self._make_format(EDITOR_COLORS["string"])
        self._rules.append((re.compile(r"'[^']*'"), str_fmt))
        self._rules.append((re.compile(r'"[^"]*"'), str_fmt))

        # Triple-quoted strings
        self._rules.append((re.compile(r'""".*?"""', re.DOTALL), str_fmt))
        self._rules.append((re.compile(r"'''.*?'''", re.DOTALL), str_fmt))

        # Comments
        cmt_fmt = self._make_format(EDITOR_COLORS["comment"], italic=True)
        self._rules.append((re.compile(r'#[^\n]*'), cmt_fmt))

        # Operators
        op_fmt = self._make_format(EDITOR_COLORS["operator"])
        self._rules.append((re.compile(r'[+\-*/%=<>!&|^~]'), op_fmt))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - match.start()
                # For patterns with groups (def name, class name), highlight the group
                if match.lastindex and match.lastindex >= 1:
                    start = match.start(1)
                    length = match.end(1) - match.start(1)
                self.setFormat(start, length, fmt)


class LineNumberArea(QWidget):
    """Line number gutter for the code editor."""

    def __init__(self, editor: CodeEditor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Enhanced QPlainTextEdit with line numbers and highlighting."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._line_number_area = LineNumberArea(self)
        self._error_lines: set[int] = set()
        self._warning_lines: set[int] = set()

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)

        self._update_line_number_area_width(0)
        self._highlight_current_line()

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits

    def _update_line_number_area_width(self, _: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def _highlight_current_line(self) -> None:
        selections = []
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor(EDITOR_COLORS["line_highlight"]))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        selections.append(selection)
        self.setExtraSelections(selections)

    def line_number_area_paint_event(self, event) -> None:
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor(EDITOR_COLORS["margin_bg"]))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                line = block_number + 1

                # Error/warning markers
                if line in self._error_lines:
                    painter.fillRect(0, top, 4, int(self.blockBoundingRect(block).height()),
                                     QColor(EDITOR_COLORS["error_marker"]))
                elif line in self._warning_lines:
                    painter.fillRect(0, top, 4, int(self.blockBoundingRect(block).height()),
                                     QColor(EDITOR_COLORS["warning_marker"]))

                painter.setPen(QColor(EDITOR_COLORS["margin_fg"]))
                painter.drawText(
                    0, top, self._line_number_area.width() - 5,
                    int(self.blockBoundingRect(block).height()),
                    Qt.AlignmentFlag.AlignRight, number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

    def set_error_lines(self, lines: set[int]) -> None:
        self._error_lines = lines
        self._line_number_area.update()

    def set_warning_lines(self, lines: set[int]) -> None:
        self._warning_lines = lines
        self._line_number_area.update()


class CodeEditorWidget(QWidget):
    """Python code editor with syntax highlighting, line numbers, and error markers."""

    code_changed = pyqtSignal(str)
    cursor_position_changed = pyqtSignal(int, int)
    run_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._current_file: Path | None = None
        self._setup_ui()
        self._setup_editor()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._editor = CodeEditor(self)
        layout.addWidget(self._editor)

    def _setup_editor(self) -> None:
        settings = get_settings()
        editor = self._editor

        # Font
        font = QFont(settings.editor.font_family, settings.editor.font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        editor.setFont(font)

        # Colors
        editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #{EDITOR_COLORS['background']:06x};
                color: #{EDITOR_COLORS['foreground']:06x};
                selection-background-color: #{EDITOR_COLORS['selection_bg']:06x};
                border: none;
                padding-left: 5px;
            }}
        """)

        # Tab width
        editor.setTabStopDistance(
            editor.fontMetrics().horizontalAdvance(' ') * settings.editor.tab_width
        )

        # Syntax highlighter
        self._highlighter = PythonHighlighter(editor.document())

    def _connect_signals(self) -> None:
        self._editor.textChanged.connect(self._on_text_changed)
        self._editor.cursorPositionChanged.connect(self._on_cursor_moved)

    def _on_text_changed(self) -> None:
        self.code_changed.emit(self.get_code())

    def _on_cursor_moved(self) -> None:
        cursor = self._editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, col)

    # Public API

    def get_code(self) -> str:
        return self._editor.toPlainText()

    def set_code(self, code: str) -> None:
        self._editor.setPlainText(code)

    def clear_markers(self) -> None:
        self._editor.set_error_lines(set())
        self._editor.set_warning_lines(set())

    def set_error_marker(self, line: int) -> None:
        self._editor._error_lines.add(line)
        self._editor._line_number_area.update()

    def set_warning_marker(self, line: int) -> None:
        self._editor._warning_lines.add(line)
        self._editor._line_number_area.update()

    def update_error_markers(self, analysis_result) -> None:
        error_lines = {e.line for e in analysis_result.errors}
        warning_lines = {w.line for w in analysis_result.warnings}
        self._editor.set_error_lines(error_lines)
        self._editor.set_warning_lines(warning_lines)

    def get_cursor_position(self) -> tuple[int, int]:
        cursor = self._editor.textCursor()
        return cursor.blockNumber() + 1, cursor.columnNumber() + 1

    @property
    def current_file(self) -> Path | None:
        return self._current_file

    @current_file.setter
    def current_file(self, path: Path | None) -> None:
        self._current_file = path

    def load_file(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        self.set_code(text)
        self._current_file = path

    def save_file(self, path: Path | None = None) -> Path | None:
        save_path = path or self._current_file
        if save_path is None:
            return None
        save_path.write_text(self.get_code(), encoding="utf-8")
        self._current_file = save_path
        return save_path

    def is_modified(self) -> bool:
        return self._editor.document().isModified()

    def set_focus(self) -> None:
        self._editor.setFocus()
