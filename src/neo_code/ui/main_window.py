"""Main application window with split-screen layout."""

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFileDialog, QMessageBox, QTabWidget, QStatusBar,
)

from neo_code.config.settings import get_settings
from neo_code.ui.code_editor import CodeEditorWidget
from neo_code.ui.editor_toolbar import EditorToolbar
from neo_code.ui.output_panel import OutputPanel
from neo_code.ui.turtle_canvas import TurtleCanvasWidget
from neo_code.ui.ai_chat_panel import AIChatPanel
from neo_code.ui.ai_input_widget import AIInputWidget
from neo_code.ui.progress_widget import ProgressWidget
from neo_code.ui.theme import MAIN_STYLESHEET
from neo_code.utils.debouncer import Debouncer
from neo_code.utils.signal_bus import SignalBus


class MainWindow(QMainWindow):
    """NEO CODE main window with split-screen IDE layout."""

    def __init__(self):
        super().__init__()
        self._settings = get_settings()
        self._bus = SignalBus.instance()
        self._setup_window()
        self._setup_ui()
        self._setup_debouncer()
        self._connect_signals()
        self._show_welcome_message()

    def _setup_window(self) -> None:
        self.setWindowTitle(f"{self._settings.name} - Educational Python IDE")
        self.resize(self._settings.ui.window_width, self._settings.ui.window_height)
        self.setMinimumSize(QSize(800, 600))
        self.setStyleSheet(MAIN_STYLESHEET)

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        self._toolbar = EditorToolbar(self)
        main_layout.addWidget(self._toolbar)

        # Main splitter (left: editor | right: AI assistant)
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # === LEFT PANEL ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Code editor
        self._editor = CodeEditorWidget()
        left_layout.addWidget(self._editor, 3)

        # Bottom tabs: Output + Turtle Canvas
        self._bottom_tabs = QTabWidget()
        self._output_panel = OutputPanel()
        self._turtle_canvas = TurtleCanvasWidget()
        self._bottom_tabs.addTab(self._output_panel, "Output")
        self._bottom_tabs.addTab(self._turtle_canvas, "Turtle Canvas")
        left_layout.addWidget(self._bottom_tabs, 1)

        self._main_splitter.addWidget(left_panel)

        # === RIGHT PANEL ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # AI Chat Panel
        self._chat_panel = AIChatPanel()
        right_layout.addWidget(self._chat_panel, 1)

        # AI Input
        self._ai_input = AIInputWidget()
        right_layout.addWidget(self._ai_input)

        # Progress Widget
        self._progress_widget = ProgressWidget()
        right_layout.addWidget(self._progress_widget)

        self._main_splitter.addWidget(right_panel)

        # Set splitter ratio
        ratio = self._settings.ui.splitter_ratio
        total = sum(ratio)
        self._main_splitter.setSizes([
            int(self.width() * ratio[0] / total),
            int(self.width() * ratio[1] / total),
        ])

        main_layout.addWidget(self._main_splitter, 1)

        # Status bar
        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #181825;
                color: #6c7086;
                font-size: 12px;
                padding: 2px 8px;
            }
        """)
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

    def _setup_debouncer(self) -> None:
        self._debouncer = Debouncer(
            delay_ms=self._settings.editor.analysis.debounce_ms,
            parent=self,
        )

    def _connect_signals(self) -> None:
        # Toolbar actions
        self._toolbar.new_clicked.connect(self._on_new)
        self._toolbar.open_clicked.connect(self._on_open)
        self._toolbar.save_clicked.connect(self._on_save)
        self._toolbar.run_clicked.connect(self._on_run)
        self._toolbar.stop_clicked.connect(self._on_stop)

        # Editor → Debouncer → Bus
        self._editor.code_changed.connect(self._debouncer.call)
        self._debouncer.triggered.connect(self._bus.code_changed.emit)
        self._editor.cursor_position_changed.connect(self._update_cursor_status)

        # AI input
        self._ai_input.question_submitted.connect(self._on_manual_question)

        # Bus signals → UI updates
        self._bus.analysis_complete.connect(self._editor.update_error_markers)
        self._bus.ai_thinking.connect(self._chat_panel.show_thinking)
        self._bus.ai_response_complete.connect(self._chat_panel.display_response)
        self._bus.ai_response_chunk.connect(self._chat_panel.append_response_chunk)
        self._bus.stdout_received.connect(self._output_panel.append_stdout)
        self._bus.stderr_received.connect(self._output_panel.append_stderr)
        self._bus.draw_command.connect(self._turtle_canvas.process_draw_command)
        self._bus.canvas_clear.connect(self._turtle_canvas.clear_canvas)
        self._bus.execution_started.connect(lambda: self._toolbar.set_running(True))
        self._bus.execution_finished.connect(lambda _: self._toolbar.set_running(False))
        self._bus.progress_updated.connect(self._progress_widget.update_profile)
        self._bus.status_message.connect(self._status_bar.showMessage)

    def _show_welcome_message(self) -> None:
        self._chat_panel.add_ai_message(
            "Welcome to **NEO CODE**! I'm **NEO TRE**, your coding assistant.\n\n"
            "Start typing Python code on the left, and I'll help you along the way!\n\n"
            "**Phase 1:** We'll learn Python basics and create amazing drawings with Turtle graphics.\n\n"
            "Try typing:\n"
            "```python\nimport turtle\nt = turtle.Turtle()\nt.forward(100)\nt.left(90)\nt.forward(100)\n```"
        )

    def _update_cursor_status(self, line: int, col: int) -> None:
        file_name = self._editor.current_file.name if self._editor.current_file else "Untitled"
        self._status_bar.showMessage(f"{file_name}  |  Line {line}, Col {col}")

    # === Toolbar Actions ===

    def _on_new(self) -> None:
        if self._editor.is_modified():
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Create new file anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return
        self._editor.set_code("")
        self._editor.current_file = None
        self._output_panel.clear()
        self._turtle_canvas.reset_turtle()

    def _on_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Python File",
            str(Path.home()),
            "Python Files (*.py);;All Files (*)",
        )
        if path:
            self._editor.load_file(Path(path))
            self._output_panel.clear()
            self._turtle_canvas.reset_turtle()
            self._status_bar.showMessage(f"Opened: {path}")

    def _on_save(self) -> None:
        if self._editor.current_file:
            self._editor.save_file()
            self._status_bar.showMessage(f"Saved: {self._editor.current_file}")
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Python File",
                str(Path.home() / "untitled.py"),
                "Python Files (*.py);;All Files (*)",
            )
            if path:
                self._editor.save_file(Path(path))
                self._status_bar.showMessage(f"Saved: {path}")

    def _on_run(self) -> None:
        code = self._editor.get_code()
        if not code.strip():
            self._status_bar.showMessage("Nothing to run")
            return

        self._output_panel.clear()
        self._output_panel.append_info("--- Running ---\n")

        # Switch to output tab if turtle not needed
        if "turtle" in code.lower():
            self._bottom_tabs.setCurrentWidget(self._turtle_canvas)
            self._turtle_canvas.reset_turtle()
        else:
            self._bottom_tabs.setCurrentWidget(self._output_panel)

        self._bus.execution_started.emit()

        # Execution will be handled by ExecutionEngine connected to bus
        # For now, basic execution via exec
        import subprocess
        import sys
        import threading

        def run_code():
            try:
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=self._settings.execution.timeout_seconds,
                )
                if result.stdout:
                    self._bus.stdout_received.emit(result.stdout)
                if result.stderr:
                    self._bus.stderr_received.emit(result.stderr)
                if result.returncode == 0:
                    self._bus.stdout_received.emit("\n--- Finished ---\n")
                else:
                    self._bus.stderr_received.emit(f"\n--- Error (code {result.returncode}) ---\n")
            except subprocess.TimeoutExpired:
                self._bus.stderr_received.emit("\n--- Timeout ---\n")
            except Exception as e:
                self._bus.stderr_received.emit(f"\n--- Error: {e} ---\n")
            finally:
                from neo_code.core.models import ExecutionResult
                self._bus.execution_finished.emit(
                    ExecutionResult(stdout="", stderr="", return_code=0, execution_time_ms=0)
                )

        thread = threading.Thread(target=run_code, daemon=True)
        thread.start()

    def _on_stop(self) -> None:
        # Will be implemented with proper ExecutionEngine
        self._toolbar.set_running(False)
        self._status_bar.showMessage("Execution stopped")

    def _on_manual_question(self, question: str) -> None:
        self._chat_panel.add_user_message(question)
        self._chat_panel.show_thinking()
        # AI assistant will handle this via bus
        # For now, simple echo response
        self._chat_panel.hide_thinking()
        self._chat_panel.add_ai_message(
            f"I received your question: *\"{question}\"*\n\n"
            "The AI assistant module will handle this when connected to Ollama."
        )

    def get_editor(self) -> CodeEditorWidget:
        return self._editor

    def get_chat_panel(self) -> AIChatPanel:
        return self._chat_panel

    def get_turtle_canvas(self) -> TurtleCanvasWidget:
        return self._turtle_canvas

    def get_output_panel(self) -> OutputPanel:
        return self._output_panel
