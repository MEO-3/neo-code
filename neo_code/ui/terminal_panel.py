"""
Terminal panel — read-only output console with "Output" header.

Connects to:
  event_bus.stdout_received  — appends plain text
  event_bus.stderr_received  — appends text in red
  event_bus.execution_started — clears the terminal
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QFrame, QToolButton, QSizePolicy
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat, QFont
from PyQt5.QtCore import pyqtSlot, Qt

from neo_code.core.event_bus import event_bus
from neo_code.theme.colors import colors


class TerminalPanel(QWidget):
    """Container: header bar titled 'Output' + read-only text view below."""

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()
        self._connect_signals()

    # ── Build ─────────────────────────────────────────────────────────────────

    _HEADER_H = 28  # px — always visible

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header (always visible) ────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(self._HEADER_H)
        header.setStyleSheet(
            f"background-color: {colors.panel_header_bg};"
            f"border-top: 1px solid {colors.border};"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 4, 0)
        header_layout.setSpacing(0)

        title = QLabel("Output")
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {colors.text_secondary};")
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Toggle button — far right of header
        self._toggle_btn = QToolButton()
        self._toggle_btn.setText("▾")
        self._toggle_btn.setToolTip("Hide output panel")
        self._toggle_btn.setFixedSize(22, 22)
        self._toggle_btn.setStyleSheet(f"""
            QToolButton {{
                color: {colors.text_secondary};
                border: none;
                border-radius: 3px;
                font-size: 13px;
            }}
            QToolButton:hover {{
                background-color: {colors.border};
            }}
        """)
        self._toggle_btn.clicked.connect(self._toggle_view)
        header_layout.addWidget(self._toggle_btn)

        layout.addWidget(header)

        # ── Text view ─────────────────────────────────────────────────────
        self._view = _OutputView()
        layout.addWidget(self._view)

        # The header must always be reachable; cap minimum height at header only.
        self.setMinimumHeight(self._HEADER_H)

    # ── Toggle ────────────────────────────────────────────────────────────────

    def _toggle_view(self) -> None:
        if self._view.isVisible():
            self._view.setVisible(False)
            # Snap the panel to just the header height so the splitter contracts.
            self.setFixedHeight(self._HEADER_H)
            self._toggle_btn.setText("▸")
            self._toggle_btn.setToolTip("Show output panel")
        else:
            self._view.setVisible(True)
            # Release the fixed height so the splitter can resize freely again.
            self.setMinimumHeight(self._HEADER_H)
            self.setMaximumHeight(16_777_215)  # Qt QWIDGETSIZE_MAX
            self._toggle_btn.setText("▾")
            self._toggle_btn.setToolTip("Hide output panel")

    # ── Signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        event_bus.execution_started.connect(self._view.clear)
        event_bus.stdout_received.connect(self._view.append_stdout)
        event_bus.stderr_received.connect(self._view.append_stderr)


class _OutputView(QPlainTextEdit):
    """The actual read-only text area inside the terminal panel."""

    def __init__(self) -> None:
        super().__init__()
        self._fmt_stdout = self._make_fmt(colors.terminal_text)
        self._fmt_stderr = self._make_fmt(colors.terminal_error)

        self.setReadOnly(True)
        self.setMaximumBlockCount(2000)
        font = QFont("Monospace", 12)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {colors.terminal_bg};
                color: {colors.terminal_text};
                border: none;
                padding: 4px;
            }}
        """)

    @staticmethod
    def _make_fmt(color: str) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        return fmt

    @pyqtSlot(str)
    def append_stdout(self, text: str) -> None:
        self._append(text, self._fmt_stdout)

    @pyqtSlot(str)
    def append_stderr(self, text: str) -> None:
        self._append(text, self._fmt_stderr)

    def _append(self, text: str, fmt: QTextCharFormat) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + "\n", fmt)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
