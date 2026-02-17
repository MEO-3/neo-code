"""Manual AI question input widget."""

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

from neo_code.ui.theme import COLORS


class AIInputWidget(QWidget):
    """Input widget for students to manually ask the AI questions."""

    question_submitted = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._input = QLineEdit(self)
        self._input.setPlaceholderText("Ask NEO TRE a question...")
        self._input.returnPressed.connect(self._submit)
        layout.addWidget(self._input, 1)

        self._send_btn = QPushButton("Send")
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
        layout.addWidget(self._send_btn)

    def _submit(self) -> None:
        text = self._input.text().strip()
        if text:
            self.question_submitted.emit(text)
            self._input.clear()
