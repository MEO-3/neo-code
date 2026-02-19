"""Manual AI question input widget with quick suggestion buttons."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QSizePolicy,
)

from neo_code.ui.theme import COLORS


# Quick suggestions: (vi_label, en_label, vi_question, en_question)
QUICK_SUGGESTIONS = [
    ("Giải thích lỗi", "Explain error", "Giải thích lỗi trong code của mình", "Explain the error in my code"),
    ("Gợi ý tiếp", "Next hint", "Cho mình thêm gợi ý", "Give me another hint"),
    ("Cho ví dụ", "Show example", "Cho mình xem ví dụ cụ thể", "Show me a specific example"),
    ("Vẽ hình gì?", "Draw what?", "Mình muốn vẽ hình nhưng không biết bắt đầu thế nào", "I want to draw a shape but don't know how to start"),
]


class AIInputWidget(QWidget):
    """Input widget for students to manually ask the AI questions."""

    question_submitted = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._lang = "vi"
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 8)
        layout.setSpacing(6)

        # Quick suggestion buttons row
        self._suggestions_layout = QHBoxLayout()
        self._suggestions_layout.setSpacing(4)
        self._suggestion_buttons: list[QPushButton] = []

        for vi_label, en_label, vi_q, en_q in QUICK_SUGGESTIONS:
            btn = QPushButton(vi_label)
            btn.setProperty("vi_label", vi_label)
            btn.setProperty("en_label", en_label)
            btn.setProperty("vi_question", vi_q)
            btn.setProperty("en_question", en_q)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    color: {COLORS['text_secondary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                    color: {COLORS['accent']};
                    border-color: {COLORS['accent']};
                }}
            """)
            btn.clicked.connect(lambda checked, b=btn: self._on_suggestion_click(b))
            self._suggestion_buttons.append(btn)
            self._suggestions_layout.addWidget(btn)

        self._suggestions_layout.addStretch()
        layout.addLayout(self._suggestions_layout)

        # Input row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self._input = QLineEdit(self)
        self._input.setPlaceholderText("Hỏi NEO TRE...")
        self._input.returnPressed.connect(self._submit)
        input_layout.addWidget(self._input, 1)

        self._send_btn = QPushButton("Gửi")
        self._send_btn.setFixedWidth(70)
        self._send_btn.clicked.connect(self._submit)
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['button_text']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
        """)
        input_layout.addWidget(self._send_btn)

        layout.addLayout(input_layout)

    def _on_suggestion_click(self, btn: QPushButton) -> None:
        """Submit the question associated with a quick suggestion button."""
        if self._lang == "vi":
            question = btn.property("vi_question")
        else:
            question = btn.property("en_question")
        if question:
            self.question_submitted.emit(question)

    def _submit(self) -> None:
        text = self._input.text().strip()
        if text:
            self.question_submitted.emit(text)
            self._input.clear()

    def set_language(self, lang: str) -> None:
        """Update UI language for placeholder and suggestion buttons."""
        self._lang = lang
        if lang == "vi":
            self._input.setPlaceholderText("Hỏi NEO TRE...")
            self._send_btn.setText("Gửi")
        else:
            self._input.setPlaceholderText("Ask NEO TRE...")
            self._send_btn.setText("Send")

        for btn in self._suggestion_buttons:
            if lang == "vi":
                btn.setText(btn.property("vi_label"))
            else:
                btn.setText(btn.property("en_label"))
