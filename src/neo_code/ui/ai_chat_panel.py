"""AI Chat Panel for displaying assistant responses."""
from __future__ import annotations

import markdown

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextBrowser, QScrollArea, QFrame,
    QSizePolicy,
)

from neo_code.core.models import AIResponse, HintLevel
from neo_code.ui.theme import COLORS


class ChatMessage(QFrame):
    """A single chat message bubble."""

    def __init__(self, content: str, is_ai: bool = True, parent: QWidget | None = None):
        super().__init__(parent)
        self._content = content
        self._is_ai = is_ai
        self._browser: QTextBrowser | None = None
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
        styled_html = self._render_markdown(content)

        self._browser = QTextBrowser(self)
        self._browser.setOpenExternalLinks(False)
        self._browser.setHtml(styled_html)
        self._browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
        """)
        self._browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._browser.document().setDocumentMargin(2)

        # Connect document size change to auto-resize
        self._browser.document().documentLayout().documentSizeChanged.connect(
            self._adjust_browser_height
        )

        layout.addWidget(self._browser)

        # Trigger initial height adjustment after layout
        QTimer.singleShot(0, self._adjust_browser_height)

    def _adjust_browser_height(self) -> None:
        """Adjust browser height to fit content."""
        if self._browser is None:
            return
        doc_height = self._browser.document().size().height()
        self._browser.setMinimumHeight(int(doc_height) + 4)
        self._browser.setMaximumHeight(int(doc_height) + 4)

    def _render_markdown(self, content: str) -> str:
        """Render markdown content to styled HTML."""
        html_content = markdown.markdown(
            content,
            extensions=["fenced_code", "codehilite", "tables"],
        )
        return f"""
        <style>
            body {{ color: {COLORS['text_primary']}; font-size: 13px;
                   font-family: "Segoe UI", "Noto Sans", sans-serif; }}
            code {{
                background-color: {COLORS['bg_tertiary']};
                padding: 2px 6px;
                border-radius: 4px;
                font-family: "JetBrains Mono", "Fira Code", monospace;
                font-size: 12px;
            }}
            pre {{
                background-color: {COLORS['bg_secondary']};
                padding: 10px;
                border-radius: 6px;
                font-family: "JetBrains Mono", "Fira Code", monospace;
                font-size: 12px;
            }}
            p {{ margin: 4px 0; }}
            a {{ color: {COLORS['accent']}; }}
        </style>
        {html_content}
        """

    def update_content(self, content: str) -> None:
        """Update the message content (for streaming)."""
        self._content = content
        if self._browser:
            self._browser.setHtml(self._render_markdown(content))
            QTimer.singleShot(0, self._adjust_browser_height)


class AIChatPanel(QWidget):
    """Panel displaying AI assistant chat messages."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._messages: list[ChatMessage] = []
        self._streaming_content: str = ""
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
        self._thinking_label = QLabel("NEO TRE is thinking...")
        self._thinking_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['warning']};
                background-color: {COLORS['bg_secondary']};
                padding: 8px 12px;
                font-style: italic;
                font-size: 12px;
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
        self._messages_layout.setContentsMargins(4, 4, 4, 4)
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

    def start_streaming_response(self) -> None:
        """Begin a new streaming AI response."""
        self._streaming_content = ""
        msg = ChatMessage("...", is_ai=True, parent=self._messages_container)
        self._messages_layout.insertWidget(self._messages_layout.count() - 1, msg)
        self._messages.append(msg)

    def append_response_chunk(self, chunk: str) -> None:
        """Append a streaming response chunk."""
        self._streaming_content += chunk
        if self._messages:
            self._messages[-1].update_content(self._streaming_content)
            self._scroll_to_bottom()

    def clear_messages(self) -> None:
        """Clear all messages."""
        for msg in self._messages:
            msg.deleteLater()
        self._messages.clear()

    def _scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the chat (deferred to allow layout update)."""
        QTimer.singleShot(50, self._do_scroll_to_bottom)

    def _do_scroll_to_bottom(self) -> None:
        vbar = self._scroll.verticalScrollBar()
        vbar.setValue(vbar.maximum())
