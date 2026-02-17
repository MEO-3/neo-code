"""Python code editor widget based on QScintilla."""

from pathlib import Path

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.Qsci import QsciScintilla, QsciLexerPython

from neo_code.ui.theme import EDITOR_COLORS
from neo_code.config.settings import get_settings


class CodeEditorWidget(QWidget):
    """Python code editor with syntax highlighting, line numbers, and error markers."""

    code_changed = pyqtSignal(str)
    cursor_position_changed = pyqtSignal(int, int)
    run_requested = pyqtSignal()

    # Marker numbers
    ERROR_MARKER = 0
    WARNING_MARKER = 1

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

        self._editor = QsciScintilla(self)
        layout.addWidget(self._editor)

    def _setup_editor(self) -> None:
        settings = get_settings()
        editor = self._editor

        # Font
        font = QFont(settings.editor.font_family, settings.editor.font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        editor.setFont(font)

        # Python lexer
        lexer = QsciLexerPython(editor)
        lexer.setFont(font)
        self._apply_lexer_colors(lexer)
        editor.setLexer(lexer)

        # Line numbers
        if settings.editor.show_line_numbers:
            editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
            editor.setMarginWidth(0, "00000")
            editor.setMarginsForegroundColor(QColor(EDITOR_COLORS["margin_fg"]))
            editor.setMarginsBackgroundColor(QColor(EDITOR_COLORS["margin_bg"]))

        # Error/warning marker margin
        editor.setMarginType(1, QsciScintilla.MarginType.SymbolMargin)
        editor.setMarginWidth(1, 16)
        editor.setMarginSensitivity(1, True)

        # Error marker (red circle)
        editor.markerDefine(QsciScintilla.MarkerSymbol.Circle, self.ERROR_MARKER)
        editor.setMarkerForegroundColor(QColor(EDITOR_COLORS["error_marker"]), self.ERROR_MARKER)
        editor.setMarkerBackgroundColor(QColor(EDITOR_COLORS["error_marker"]), self.ERROR_MARKER)

        # Warning marker (yellow triangle)
        editor.markerDefine(QsciScintilla.MarkerSymbol.Triangle, self.WARNING_MARKER)
        editor.setMarkerForegroundColor(
            QColor(EDITOR_COLORS["warning_marker"]), self.WARNING_MARKER
        )
        editor.setMarkerBackgroundColor(
            QColor(EDITOR_COLORS["warning_marker"]), self.WARNING_MARKER
        )

        # Editor appearance
        editor.setColor(QColor(EDITOR_COLORS["foreground"]))
        editor.setPaper(QColor(EDITOR_COLORS["background"]))
        editor.setCaretForegroundColor(QColor(EDITOR_COLORS["caret"]))
        editor.setSelectionBackgroundColor(QColor(EDITOR_COLORS["selection_bg"]))

        # Current line highlight
        if settings.editor.highlight_current_line:
            editor.setCaretLineVisible(True)
            editor.setCaretLineBackgroundColor(QColor(EDITOR_COLORS["line_highlight"]))

        # Indentation
        editor.setIndentationsUseTabs(False)
        editor.setTabWidth(settings.editor.tab_width)
        editor.setAutoIndent(settings.editor.auto_indent)
        editor.setIndentationGuides(True)

        # Brace matching
        editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        editor.setMatchedBraceForegroundColor(QColor(EDITOR_COLORS["brace_match_fg"]))
        editor.setMatchedBraceBackgroundColor(QColor(EDITOR_COLORS["brace_match_bg"]))

        # Folding
        editor.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        editor.setFoldMarginColors(
            QColor(EDITOR_COLORS["fold_margin_bg"]),
            QColor(EDITOR_COLORS["fold_margin_bg"]),
        )

        # Word wrap
        if settings.editor.word_wrap:
            editor.setWrapMode(QsciScintilla.WrapMode.WrapWord)

        # Edge column
        editor.setEdgeMode(QsciScintilla.EdgeMode.EdgeNone)

        # Encoding
        editor.setUtf8(True)

    def _apply_lexer_colors(self, lexer: QsciLexerPython) -> None:
        """Apply theme colors to the Python lexer."""
        lexer.setColor(QColor(EDITOR_COLORS["foreground"]))
        lexer.setPaper(QColor(EDITOR_COLORS["background"]))

        # Python-specific token colors
        color_map = {
            QsciLexerPython.Keyword: EDITOR_COLORS["keyword"],
            QsciLexerPython.DoubleQuotedString: EDITOR_COLORS["string"],
            QsciLexerPython.SingleQuotedString: EDITOR_COLORS["string"],
            QsciLexerPython.TripleSingleQuotedString: EDITOR_COLORS["string"],
            QsciLexerPython.TripleDoubleQuotedString: EDITOR_COLORS["string"],
            QsciLexerPython.Number: EDITOR_COLORS["number"],
            QsciLexerPython.Comment: EDITOR_COLORS["comment"],
            QsciLexerPython.CommentBlock: EDITOR_COLORS["comment"],
            QsciLexerPython.Decorator: EDITOR_COLORS["decorator"],
            QsciLexerPython.FunctionMethodName: EDITOR_COLORS["function_name"],
            QsciLexerPython.ClassName: EDITOR_COLORS["class_name"],
            QsciLexerPython.Operator: EDITOR_COLORS["operator"],
            QsciLexerPython.HighlightedIdentifier: EDITOR_COLORS["builtin"],
        }

        for token_type, color in color_map.items():
            lexer.setColor(QColor(color), token_type)
            lexer.setPaper(QColor(EDITOR_COLORS["background"]), token_type)

    def _connect_signals(self) -> None:
        self._editor.textChanged.connect(self._on_text_changed)
        self._editor.cursorPositionChanged.connect(self._on_cursor_moved)

    def _on_text_changed(self) -> None:
        self.code_changed.emit(self.get_code())

    def _on_cursor_moved(self, line: int, col: int) -> None:
        self.cursor_position_changed.emit(line + 1, col + 1)

    # Public API

    def get_code(self) -> str:
        """Get the current code content."""
        return self._editor.text()

    def set_code(self, code: str) -> None:
        """Set the editor content."""
        self._editor.setText(code)

    def clear_markers(self) -> None:
        """Clear all error/warning markers."""
        self._editor.markerDeleteAll(self.ERROR_MARKER)
        self._editor.markerDeleteAll(self.WARNING_MARKER)

    def set_error_marker(self, line: int) -> None:
        """Set an error marker on the given line (1-indexed)."""
        self._editor.markerAdd(line - 1, self.ERROR_MARKER)

    def set_warning_marker(self, line: int) -> None:
        """Set a warning marker on the given line (1-indexed)."""
        self._editor.markerAdd(line - 1, self.WARNING_MARKER)

    def update_error_markers(self, analysis_result) -> None:
        """Update markers from an AnalysisResult."""
        self.clear_markers()
        for error in analysis_result.errors:
            self.set_error_marker(error.line)
        for warning in analysis_result.warnings:
            self.set_warning_marker(warning.line)

    def get_cursor_position(self) -> tuple[int, int]:
        """Get cursor position as (line, column), 1-indexed."""
        line, col = self._editor.getCursorPosition()
        return line + 1, col + 1

    @property
    def current_file(self) -> Path | None:
        return self._current_file

    @current_file.setter
    def current_file(self, path: Path | None) -> None:
        self._current_file = path

    def load_file(self, path: Path) -> None:
        """Load a file into the editor."""
        text = path.read_text(encoding="utf-8")
        self.set_code(text)
        self._current_file = path

    def save_file(self, path: Path | None = None) -> Path | None:
        """Save editor content to file. Returns the saved path."""
        save_path = path or self._current_file
        if save_path is None:
            return None
        save_path.write_text(self.get_code(), encoding="utf-8")
        self._current_file = save_path
        return save_path

    def is_modified(self) -> bool:
        """Check if the editor content has been modified."""
        return self._editor.isModified()

    def set_focus(self) -> None:
        """Set keyboard focus to the editor."""
        self._editor.setFocus()
