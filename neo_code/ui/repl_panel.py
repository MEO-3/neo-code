"""
REPL panel — live Python interactive console.

Starts `python3 -u -i` on show, kills it on hide.
"""

import re
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPlainTextEdit, QLineEdit, QToolButton,
)
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat, QFont
from PyQt5.QtCore import QProcess, pyqtSlot, Qt

from neo_code.theme.colors import colors

# Strip ANSI CSI sequences, OSC sequences (incl. OSC 633 shell-integration),
# and readline bracket markers (\x01/\x02) that Python -i can emit via stderr.
_CTRL_RE = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]"   # CSI:  ESC [ ... final-byte
    r"|\x1b\][^\x07\x1b]*\x07"   # OSC:  ESC ] ... BEL
    r"|\x1b\][^\x1b]*\x1b\\"     # OSC:  ESC ] ... ST
    r"|\x1b[@-Z\\-_]"            # Fe:   ESC single-char
    r"|[\x01\x02\x07\x0f\x0e]"   # SOH, STX, BEL, SI, SO
)


class ReplPanel(QWidget):
    """
    Live Python REPL console.
    Starts `python3 -u -i` on show, kills it on hide.
    """

    def __init__(self) -> None:
        super().__init__()
        self._process: QProcess | None = None
        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Output view
        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        self._output.setMaximumBlockCount(2000)
        font = QFont("Monospace", 12)
        font.setStyleHint(QFont.Monospace)
        self._output.setFont(font)
        self._output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {colors.terminal_bg};
                color: {colors.terminal_text};
                border: none;
                padding: 4px;
            }}
        """)
        layout.addWidget(self._output)

        # Formats
        self._fmt_echo = self._make_fmt(colors.primary)
        self._fmt_stdout = self._make_fmt(colors.terminal_text)
        self._fmt_stderr = self._make_fmt(colors.terminal_error)

        # Input row
        input_row = QWidget()
        input_row.setStyleSheet(
            f"background-color: {colors.terminal_bg};"
            f"border-top: 1px solid {colors.border};"
        )
        row_layout = QHBoxLayout(input_row)
        row_layout.setContentsMargins(8, 4, 8, 4)
        row_layout.setSpacing(4)

        prompt = QLabel(">>> ")
        prompt.setFont(font)
        prompt.setStyleSheet(f"color: {colors.primary}; background: transparent; border: none;")
        row_layout.addWidget(prompt)

        self._input = QLineEdit()
        self._input.setFont(font)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                color: {colors.terminal_text};
                border: none;
                selection-background-color: {colors.primary};
            }}
        """)
        self._input.returnPressed.connect(self._submit)
        row_layout.addWidget(self._input)

        submit_btn = QToolButton()
        submit_btn.setText("↵")
        submit_btn.setToolTip("Gửi lệnh (Enter)")
        submit_btn.setFixedSize(26, 26)
        submit_btn.setStyleSheet(f"""
            QToolButton {{
                color: {colors.terminal_text};
                background: transparent;
                border: 1px solid {colors.border};
                border-radius: 3px;
                font-size: 14px;
            }}
            QToolButton:hover {{
                background-color: {colors.surface_alt};
            }}
        """)
        submit_btn.clicked.connect(self._submit)
        row_layout.addWidget(submit_btn)

        layout.addWidget(input_row)

    # ── Process lifecycle ──────────────────────────────────────────────────────

    def _start_process(self) -> None:
        if self._process is not None and self._process.state() != QProcess.NotRunning:
            return
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.SeparateChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        self._output.clear()
        self._input.setEnabled(True)
        self._process.start(sys.executable, ["-u", "-i"])

    def _stop_process(self) -> None:
        if self._process is None:
            return
        if self._process.state() != QProcess.NotRunning:
            self._process.kill()
            self._process.waitForFinished(500)
        self._process = None

    # ── Qt events ─────────────────────────────────────────────────────────────

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._start_process()
        self._input.setFocus()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self._stop_process()

    # ── Slots ─────────────────────────────────────────────────────────────────

    @pyqtSlot()
    def _on_stdout(self) -> None:
        if self._process is None:
            return
        raw = self._process.readAllStandardOutput().data().decode(errors="replace")
        text = _CTRL_RE.sub("", raw)
        if text.strip():
            self._append(text, self._fmt_stdout)

    @pyqtSlot()
    def _on_stderr(self) -> None:
        if self._process is None:
            return
        raw = self._process.readAllStandardError().data().decode(errors="replace")
        text = _CTRL_RE.sub("", raw)
        filtered = self._filter_stderr(text)
        if filtered:
            self._append(filtered, self._fmt_stderr)

    # Python -i writes prompts and startup banner to stderr — drop them.
    # Real tracebacks pass through unchanged.
    _STDERR_SKIP_STARTSWITH = (
        "Python ",     # version banner
        "[GCC ",
        "[Clang ",
        'Type "help"',
        'Type "copyright"',
    )

    @classmethod
    def _filter_stderr(cls, text: str) -> str:
        kept = []
        for line in text.splitlines():
            s = line.strip()
            if s in (">>>", "...", ">>> ", "... "):
                continue
            if any(s.startswith(p) for p in cls._STDERR_SKIP_STARTSWITH):
                continue
            kept.append(line)
        return "\n".join(kept)

    @pyqtSlot(int, QProcess.ExitStatus)
    def _on_finished(self, _code: int, _status) -> None:
        self._append("[Phiên tương tác đã kết thúc]", self._fmt_stderr)
        self._input.setEnabled(False)

    @pyqtSlot()
    def _submit(self) -> None:
        text = self._input.text()
        self._input.clear()
        self._append(">>> " + text, self._fmt_echo)
        if self._process and self._process.state() == QProcess.Running:
            self._process.write((text + "\n").encode())

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _make_fmt(color: str) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        return fmt

    def _append(self, text: str, fmt: QTextCharFormat) -> None:
        # Strip trailing newline — insertText adds its own spacing
        text = text.rstrip("\n")
        if not text:
            return
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + "\n", fmt)
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()
