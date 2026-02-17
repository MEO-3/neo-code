"""AI Chat Panel for displaying assistant responses."""

import markdown

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextBrowser, QScrollArea, QFrame,
)

from neo_code.core.models import AIResponse, HintLevel
from neo_code.ui.theme import COLORS


class ChatMessage(QFrame):
    """A single chat message bubble."""

    def __init__(self, content: str, is_ai: bool = True, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui(content, is_ai)

    def _setup_ui(self, content: str, is_ai: bool) -> None:
        bg = COLORS["chat_ai_bg"] if is_ai else COLORS["chat_user_bg"]
        border_color = COLORS["accent"] if is_ai else COLORS["border"]
        role_label = "NEO TRE" if is_ai else "Student"
        role_color = COLORS["accent"] if is_ai else COLORS["success"]

        self.setStyleSheet(f"""
            ChatMessage {{
                background-color: {bg};
                border-left: 3px solid {border_color};
                border-radius: 8px;
                margin: 4px 8px;
                padding: 0px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Role label
        role = QLabel(role_label)
        role.setStyleSheet(f"color: {role_color}; font-weight: bold; font-size: 11px;")
        layout.addWidget(role)

        # Content (markdown rendered)
        html_content = markdown.markdown(
            content,
            extensions=["fenced_code", "codehilite", "tables"],
        )

        # Style the rendered HTML
        styled_html = f"""
        <style>
            body {{ color: {COLORS['text_primary']}; font-size: 13px; }}
            code {{
                background-color: {COLORS['bg_tertiary']};
                padding: 2px 6px;
                border-radius: 4px;
                font-family: "JetBrains Mono", monospace;
                font-size: 12px;
            }}
            pre {{
                background-color: {COLORS['bg_secondary']};
                padding: 10px;
                border-radius: 6px;
                font-family: "JetBrains Mono", monospace;
                font-size: 12px;
            }}
            a {{ color: {COLORS['accent']}; }}
        </style>
        {html_content}
        """

        content_browser = QTextBrowser(self)
        content_browser.setOpenExternalLinks(False)
        content_browser.setHtml(styled_html)
        content_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
        """)
        # Auto-resize based on content
        content_browser.document().setDocumentMargin(0)
        doc_height = content_browser.document().size().height()
        content_browser.setFixedHeight(int(doc_height) + 10)

        layout.addWidget(content_browser)


class AIChatPanel(QWidget):
    """Panel displaying AI assistant chat messages."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._messages: list[ChatMessage] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QLabel("NEO TRE Assistant")
        header.setObjectName("sectionTitle")
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['toolbar_bg']};
                padding: 8px 12px;
                font-size: 15px;
                font-weight: bold;
                color: {COLORS['accent']};
            }}
        """)
        layout.addWidget(header)

        # Thinking indicator
        self._thinking_label = QLabel("Thinking...")
        self._thinking_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_dim']};
                padding: 8px 12px;
                font-style: italic;
            }}
        """)
        self._thinking_label.hide()
        layout.addWidget(self._thinking_label)

        # Scroll area for messages
        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['chat_bg']};
                border: none;
            }}
        """)

        self._messages_container = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_container)
        self._messages_layout.setContentsMargins(0, 4, 0, 4)
        self._messages_layout.setSpacing(8)
        self._messages_layout.addStretch()

        self._scroll.setWidget(self._messages_container)
        layout.addWidget(self._scroll, 1)

    def add_ai_message(self, content: str) -> None:
        """Add an AI assistant message."""
        msg = ChatMessage(content, is_ai=True, parent=self._messages_container)
        self._messages_layout.insertWidget(self._messages_layout.count() - 1, msg)
        self._messages.append(msg)
        self._scroll_to_bottom()

    def add_user_message(self, content: str) -> None:
        """Add a student message."""
        msg = ChatMessage(content, is_ai=False, parent=self._messages_container)
        self._messages_layout.insertWidget(self._messages_layout.count() - 1, msg)
        self._messages.append(msg)
        self._scroll_to_bottom()

    def display_response(self, response: AIResponse) -> None:
        """Display a structured AI response."""
        self.hide_thinking()

        # Build message with hint level indicator
        level_labels = {
            HintLevel.NUDGE: "Hint",
            HintLevel.GUIDANCE: "Guidance",
            HintLevel.EXPLICIT: "Detailed Help",
            HintLevel.SOLUTION: "Solution",
        }
        prefix = ""
        if response.is_encouragement:
            prefix = "Great job! "
        elif response.is_error_explanation:
            level_text = level_labels.get(response.hint_level, "")
            prefix = f"**[{level_text}]** " if level_text else ""

        content = prefix + response.message

        if response.code_suggestion:
            content += f"\n\n```python\n{response.code_suggestion}\n```"

        self.add_ai_message(content)

    def show_thinking(self) -> None:
        """Show the thinking indicator."""
        self._thinking_label.show()

    def hide_thinking(self) -> None:
        """Hide the thinking indicator."""
        self._thinking_label.hide()

    def append_response_chunk(self, chunk: str) -> None:
        """Append a streaming response chunk (for incremental display)."""
        # For streaming, we update the last AI message or create a new one
        if self._messages and isinstance(self._messages[-1], ChatMessage):
            # In a production version, we'd update the last message content
            # For now, we'll accumulate and display at once
            pass

    def clear_messages(self) -> None:
        """Clear all messages."""
        for msg in self._messages:
            msg.deleteLater()
        self._messages.clear()

    def _scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the chat."""
        vbar = self._scroll.verticalScrollBar()
        vbar.setValue(vbar.maximum())
