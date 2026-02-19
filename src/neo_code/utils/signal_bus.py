"""Application-wide signal bus for decoupled component communication."""
from __future__ import annotations


from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """Centralized signal hub for cross-component communication.


    Allows components to communicate without direct references to each other.

    Usage:
        bus = SignalBus.instance()
        bus.code_changed.connect(my_handler)
        bus.code_changed.emit("print('hello')")
    """

    # Editor signals
    code_changed = pyqtSignal(str)
    file_opened = pyqtSignal(str)
    file_saved = pyqtSignal(str)
    cursor_moved = pyqtSignal(int, int)  # line, column

    # Execution signals
    execution_started = pyqtSignal()
    execution_finished = pyqtSignal(object)  # ExecutionResult
    stdout_received = pyqtSignal(str)
    stderr_received = pyqtSignal(str)

    # Analysis signals
    analysis_complete = pyqtSignal(object)  # AnalysisResult

    # AI signals
    ai_thinking = pyqtSignal()
    ai_response_chunk = pyqtSignal(str)
    ai_response_complete = pyqtSignal(object)  # AIResponse
    ai_error = pyqtSignal(str)

    # Turtle signals
    draw_command = pyqtSignal(object)  # DrawCommand
    canvas_clear = pyqtSignal()

    # Robot Arena signals
    robot_command = pyqtSignal(object)  # RobotCommand
    arena_clear = pyqtSignal()

    # Education signals
    phase_changed = pyqtSignal(int)
    lesson_changed = pyqtSignal(int)
    exercise_loaded = pyqtSignal(str)
    progress_updated = pyqtSignal(object)  # StudentProfile

    # Application signals
    settings_changed = pyqtSignal()
    status_message = pyqtSignal(str)

    _instance: "SignalBus | None" = None

    @classmethod
    def instance(cls) -> "SignalBus":
        """Get the singleton SignalBus instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        cls._instance = None
