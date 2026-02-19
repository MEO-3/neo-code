"""Conversation history management for the AI assistant."""
from __future__ import annotations


from dataclasses import dataclass, field
from typing import Optional

from neo_code.config.settings import get_settings


@dataclass
class ChatTurn:
    """A single turn in the conversation."""

    role: str  # "user" or "assistant"
    content: str


class ConversationHistory:
    """Manages conversation history with token window management."""

    def __init__(self):
        self._settings = get_settings()
        self._turns: list[ChatTurn] = []
        self._max_turns = self._settings.ai.context.max_history_turns

    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        self._turns.append(ChatTurn(role="user", content=content))
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        self._turns.append(ChatTurn(role="assistant", content=content))
        self._trim()

    def get_messages(self) -> list[dict[str, str]]:
        """Get conversation history as a list of message dicts for the LLM."""
        return [{"role": t.role, "content": t.content} for t in self._turns]

    def get_context_summary(self) -> str:
        """Get a brief summary of recent conversation for context."""
        if not self._turns:
            return "No previous conversation."

        recent = self._turns[-4:]  # Last 2 exchanges
        lines = []
        for turn in recent:
            prefix = "Student" if turn.role == "user" else "NEO TRE"
            # Truncate long messages
            content = turn.content[:150]
            if len(turn.content) > 150:
                content += "..."
            lines.append(f"{prefix}: {content}")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all history."""
        self._turns.clear()

    def _trim(self) -> None:
        """Keep only the most recent turns."""
        if len(self._turns) > self._max_turns * 2:
            self._turns = self._turns[-(self._max_turns * 2):]

    @property
    def turn_count(self) -> int:
        return len(self._turns)
