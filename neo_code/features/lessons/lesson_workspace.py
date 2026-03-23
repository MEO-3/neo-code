from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPlainTextEdit,
    QFrame, QSizePolicy,
)
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import pyqtSlot

from neo_code.core.event_bus import event_bus
from neo_code.theme.colors import colors


class LessonWorkspacePanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        goal, self._goal_body = self._card(
            "🎯 Mục tiêu",
            "Hãy làm cho máy tính nói 'Xin chào'.",
        )
        layout.addWidget(goal)

        hint, self._hint_body = self._card(
            "💡 Gợi ý",
            "Dùng hàm print() để hiển thị văn bản.",
        )
        layout.addWidget(hint)

        font = QFont("Monospace", 12)
        font.setStyleHint(QFont.Monospace)

        output = QFrame()
        output.setStyleSheet(
            f"background-color: {colors.surface};"
            f"border: 1px solid {colors.border};"
            "border-radius: 6px;"
        )
        output_layout = QVBoxLayout(output)
        output_layout.setContentsMargins(10, 8, 10, 10)
        output_layout.setSpacing(8)

        output_title = QLabel("📺 Kết quả")
        output_title.setFont(self._title_font())
        output_title.setStyleSheet(f"color: {colors.text};")
        output_layout.addWidget(output_title)

        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        self._output.setStyleSheet(
            f"background-color: {colors.terminal_bg};"
            f"color: {colors.terminal_text};"
            "border: none;"
            "border-radius: 4px;"
        )
        self._output.setFont(font)
        self._output.setMaximumBlockCount(1000)
        output_layout.addWidget(self._output)

        self._fmt_stdout = self._make_fmt(colors.terminal_text)
        self._fmt_stderr = self._make_fmt(colors.terminal_error)

        layout.addWidget(output)

        feedback = QFrame()
        feedback.setStyleSheet(
            f"background-color: {colors.surface};"
            f"border: 1px solid {colors.border};"
            "border-radius: 6px;"
        )
        feedback_layout = QVBoxLayout(feedback)
        feedback_layout.setContentsMargins(10, 8, 10, 10)
        feedback_layout.setSpacing(6)

        feedback_title = QLabel("✅ Phản hồi")
        feedback_title.setFont(self._title_font())
        feedback_title.setStyleSheet(f"color: {colors.text};")
        feedback_layout.addWidget(feedback_title)

        self._feedback_body = QLabel("Chưa chạy bài.")
        self._feedback_body.setWordWrap(True)
        self._feedback_body.setStyleSheet(f"color: {colors.text_secondary};")
        feedback_layout.addWidget(self._feedback_body)

        feedback.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(feedback)

        starter = QFrame()
        starter.setStyleSheet(
            f"background-color: {colors.surface};"
            f"border: 1px solid {colors.border};"
            "border-radius: 6px;"
        )
        starter_layout = QVBoxLayout(starter)
        starter_layout.setContentsMargins(10, 8, 10, 10)
        starter_layout.setSpacing(8)

        starter_title = QLabel("🧩 Mã gợi ý")
        starter_title.setFont(self._title_font())
        starter_title.setStyleSheet(f"color: {colors.text};")
        starter_layout.addWidget(starter_title)

        self._starter_code = QPlainTextEdit()
        self._starter_code.setReadOnly(True)
        self._starter_code.setStyleSheet(
            f"background-color: {colors.editor_bg};"
            f"color: {colors.editor_text};"
            f"border: 1px solid {colors.border};"
            "border-radius: 4px;"
        )
        self._starter_code.setFont(font)
        self._starter_code.setMaximumBlockCount(200)
        starter_layout.addWidget(self._starter_code)

        layout.addWidget(starter)

    def _connect_signals(self) -> None:
        event_bus.execution_started.connect(self._on_execution_started)
        event_bus.execution_finished.connect(self._on_execution_finished)
        event_bus.stdout_received.connect(self._on_stdout)
        event_bus.stderr_received.connect(self._on_stderr)

    def _set_feedback(self, text: str, success: bool | None = None) -> None:
        if success is None:
            color = colors.text_secondary
        else:
            color = colors.run_bg if success else colors.terminal_error
        self._feedback_body.setStyleSheet(f"color: {color};")
        self._feedback_body.setText(text)

    def _append(self, text: str, fmt: QTextCharFormat) -> None:
        text = text.rstrip("\n")
        if not text:
            return
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + "\n", fmt)
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()

    @staticmethod
    def _make_fmt(color: str) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        return fmt

    def _card(self, title: str, body: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {colors.surface};"
            f"border: 1px solid {colors.border};"
            "border-radius: 6px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setFont(self._title_font())
        title_lbl.setStyleSheet(f"color: {colors.text};")
        layout.addWidget(title_lbl)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(f"color: {colors.text_secondary};")
        layout.addWidget(body_lbl)

        return card, body_lbl

    def set_lesson(self, lesson: dict) -> None:
        challenge = lesson.get("challenge", {})
        self._goal_body.setText(challenge.get("goal", ""))
        self._hint_body.setText(challenge.get("hint", ""))
        self._starter_code.setPlainText(challenge.get("starter_code", ""))
        self._output.clear()
        self._set_feedback("Viết code trong trình soạn thảo chính rồi bấm Chạy.", None)

    @pyqtSlot()
    def _on_execution_started(self) -> None:
        if not self.isVisible():
            return
        self._output.clear()
        self._set_feedback("Đang chạy...", None)

    @pyqtSlot(int)
    def _on_execution_finished(self, exit_code: int) -> None:
        if not self.isVisible():
            return
        if exit_code == 0:
            self._set_feedback("Hoàn thành. Hãy kiểm tra kết quả nhé!", True)
        else:
            self._set_feedback("Có lỗi xảy ra. Hãy thử lại.", False)

    @pyqtSlot(str)
    def _on_stdout(self, text: str) -> None:
        if not self.isVisible():
            return
        self._append(text, self._fmt_stdout)

    @pyqtSlot(str)
    def _on_stderr(self, text: str) -> None:
        if not self.isVisible():
            return
        self._append(text, self._fmt_stderr)

    @staticmethod
    def _title_font() -> QFont:
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        return font
