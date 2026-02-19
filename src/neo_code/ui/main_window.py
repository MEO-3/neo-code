"""Main application window with split-screen layout."""
from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFileDialog, QMessageBox, QTabWidget, QStatusBar, QMenu,
)

from neo_code.config.settings import get_settings
from neo_code.ui.code_editor import CodeEditorWidget
from neo_code.ui.editor_toolbar import EditorToolbar
from neo_code.ui.output_panel import OutputPanel
from neo_code.ui.turtle_canvas import TurtleCanvasWidget
from neo_code.ui.robot_arena_canvas import RobotArenaWidget
from neo_code.ui.ai_chat_panel import AIChatPanel
from neo_code.ui.ai_input_widget import AIInputWidget
from neo_code.ui.progress_widget import ProgressWidget
from neo_code.ui.theme import MAIN_STYLESHEET
from neo_code.utils.debouncer import Debouncer
from neo_code.utils.signal_bus import SignalBus
from neo_code.core.execution_engine import ExecutionWorker
from neo_code.core.turtle_interpreter import (
    generate_turtle_wrapper_code,
    parse_turtle_output_line,
)
from neo_code.core.robot_interpreter import (
    generate_robot_wrapper_code,
    parse_robot_output_line,
)
from neo_code.core.models import AnalysisResult, AIResponse, ExecutionResult
from neo_code.ai.assistant_service import AIAssistantService
from neo_code.education.hints.common_errors import get_rule_based_hint
from neo_code.education.projects import PROJECTS, get_projects_by_category

logger = logging.getLogger(__name__)

# Level display names
LEVEL_NAMES = {
    1: "Level 1: Kham pha",
    2: "Level 2: Lap trinh vien",
    3: "Level 3: Chuyen gia",
}


class AIQueryWorker(QThread):
    """Background thread for AI queries (manual questions and auto-analysis)."""

    response_ready = pyqtSignal(object)  # AIResponse
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._task = None  # callable that returns AIResponse | None

    def set_task(self, task):
        """Set the callable task to run in the background."""
        self._task = task

    def run(self) -> None:
        if self._task is None:
            return
        try:
            result = self._task()
            if result is not None:
                self.response_ready.emit(result)
        except Exception as e:
            logger.error(f"AI query error: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self._task = None


class MainWindow(QMainWindow):
    """NEO CODE main window with split-screen IDE layout."""

    def __init__(self):
        super().__init__()
        self._settings = get_settings()
        self._bus = SignalBus.instance()
        self._execution_worker: ExecutionWorker | None = None
        self._ai_worker: AIQueryWorker | None = None
        self._has_turtle = False
        self._has_robot = False

        # AI assistant service
        self._ai_service = AIAssistantService()
        self._last_analysis: AnalysisResult | None = None
        self._current_code: str = ""

        # Level system
        self._current_level: int = 1
        self._first_launch = True
        self._current_field_id: str = ""

        self._setup_window()
        self._setup_ui()
        self._setup_debouncer()
        self._connect_signals()
        self._show_welcome_message()

        # Auto-show level selector on first launch
        QTimer.singleShot(500, self._check_first_launch)

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

        # Bottom tabs: Output + Turtle Canvas + Robot Arena
        self._bottom_tabs = QTabWidget()
        self._output_panel = OutputPanel()
        self._turtle_canvas = TurtleCanvasWidget()
        self._robot_arena = RobotArenaWidget()
        self._bottom_tabs.addTab(self._output_panel, "Output")
        self._bottom_tabs.addTab(self._turtle_canvas, "Turtle Canvas")
        self._bottom_tabs.addTab(self._robot_arena, "Robot Arena")
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
        self._toolbar.samples_clicked.connect(self._on_samples)
        self._toolbar.level_clicked.connect(self._on_level_selector)
        self._toolbar.language_changed.connect(self._on_language_changed)

        # Editor → track code + Debouncer → Bus (for code analysis)
        self._editor.code_changed.connect(self._on_code_changed)
        self._debouncer.triggered.connect(self._bus.code_changed.emit)
        self._editor.cursor_position_changed.connect(self._update_cursor_status)

        # Analysis complete → AI auto-analysis is handled in _on_analysis_complete
        self._bus.analysis_complete.connect(self._on_analysis_complete)

        # AI input
        self._ai_input.question_submitted.connect(self._on_manual_question)

        # Bus signals → UI updates
        self._bus.ai_thinking.connect(self._chat_panel.show_thinking)
        self._bus.ai_response_complete.connect(self._chat_panel.display_response)
        self._bus.ai_response_chunk.connect(self._chat_panel.append_response_chunk)
        self._bus.stdout_received.connect(self._output_panel.append_stdout)
        self._bus.stderr_received.connect(self._output_panel.append_stderr)
        self._bus.draw_command.connect(self._turtle_canvas.process_draw_command)
        self._bus.canvas_clear.connect(self._turtle_canvas.clear_canvas)
        self._bus.robot_command.connect(self._robot_arena.process_robot_command)
        self._bus.arena_clear.connect(self._robot_arena.reset_arena)
        self._bus.execution_started.connect(lambda: self._toolbar.set_running(True))
        self._bus.execution_finished.connect(lambda _: self._toolbar.set_running(False))
        self._bus.progress_updated.connect(self._progress_widget.update_profile)
        self._bus.status_message.connect(self._status_bar.showMessage)

    def _show_welcome_message(self) -> None:
        # Show AI model status
        model_info = self._ai_service._llm.get_model_info()
        if model_info["available"]:
            ai_status = f"AI: **{model_info['model']}**"
        else:
            ai_status = "AI: **Offline mode** (rule-based hints)"

        self._chat_panel.add_ai_message(
            "Chao mung ban den voi **NEO CODE**! Minh la **NEO TRE**, tro ly lap trinh cua ban.\n\n"
            "Hay viet code Python o ben trai, minh se ho tro ban!\n\n"
            "**Bat dau nhanh:** Bam nut **Samples** de chon bai mau, "
            "hoac thu go:\n"
            "```python\nimport turtle\nt = turtle.Turtle()\nt.forward(100)\nt.left(90)\nt.forward(100)\n```\n\n"
            "Bam **Run** de chay code. Ban co the **hoi minh bat cu luc nao** - "
            "dung o chat ben duoi hoac bam nut goi y nhanh!\n\n"
            f"*{ai_status}*"
        )

    def _check_first_launch(self) -> None:
        """Show level selector on first launch."""
        if self._first_launch:
            self._first_launch = False
            self._on_level_selector()

    def _update_cursor_status(self, line: int, col: int) -> None:
        file_name = self._editor.current_file.name if self._editor.current_file else "Untitled"
        self._status_bar.showMessage(f"{file_name}  |  Line {line}, Col {col}")

    # === Code tracking ===

    def _on_code_changed(self, code: str) -> None:
        """Track current code for AI context."""
        self._current_code = code
        self._debouncer.call(code)

    def _on_analysis_complete(self, analysis: AnalysisResult) -> None:
        """Handle analysis results: update markers + trigger AI feedback."""
        self._editor.update_error_markers(analysis)
        self._last_analysis = analysis

        # Run AI auto-analysis in background
        code = self._current_code
        service = self._ai_service

        def ai_task():
            return service.on_code_changed(code, analysis)

        self._run_ai_task(ai_task)

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
        self._robot_arena.reset_arena()

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
            self._robot_arena.reset_arena()
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

        # Stop any previous execution
        if self._execution_worker and self._execution_worker.isRunning():
            self._execution_worker.stop()
            self._execution_worker.wait(2000)

        self._output_panel.clear()
        self._output_panel.append_info("--- Running ---\n")

        # Detect turtle or robot usage and prepend wrapper
        self._has_turtle = "turtle" in code.lower()
        self._has_robot = "import robot" in code or "from robot" in code
        if self._has_robot:
            self._bottom_tabs.setCurrentWidget(self._robot_arena)
            self._robot_arena.reset_arena()
            exec_code = generate_robot_wrapper_code() + "\n" + code
        elif self._has_turtle:
            self._bottom_tabs.setCurrentWidget(self._turtle_canvas)
            self._turtle_canvas.reset_turtle()
            exec_code = generate_turtle_wrapper_code() + "\n" + code
        else:
            self._bottom_tabs.setCurrentWidget(self._output_panel)
            exec_code = code

        # Create and wire up execution worker
        self._execution_worker = ExecutionWorker(self)
        self._execution_worker.stdout_received.connect(self._on_stdout_line)
        self._execution_worker.stderr_received.connect(self._bus.stderr_received.emit)
        self._execution_worker.execution_started.connect(self._bus.execution_started.emit)
        self._execution_worker.execution_finished.connect(self._on_execution_finished)
        self._execution_worker.execute(exec_code)

    def _on_stdout_line(self, text: str) -> None:
        """Handle stdout, routing turtle/robot commands to canvas."""
        for line in text.splitlines(keepends=True):
            stripped = line.strip()
            if stripped.startswith("__NEO_TURTLE_LIMIT__:"):
                limit = stripped.split(":")[1]
                self._output_panel.append_stderr(
                    f"\n⚠ Đã vượt giới hạn {limit} lệnh turtle! "
                    f"Hãy giảm số lần lặp lại.\n"
                    f"⚠ Exceeded {limit} turtle command limit! "
                    f"Reduce your loop count.\n"
                )
            elif stripped.startswith("__NEO_ROBOT_LIMIT__:"):
                limit = stripped.split(":")[1]
                self._output_panel.append_stderr(
                    f"\n⚠ Đã vượt giới hạn {limit} lệnh robot! "
                    f"Hãy giảm số lần lặp lại.\n"
                    f"⚠ Exceeded {limit} robot command limit! "
                    f"Reduce your loop count.\n"
                )
            elif stripped.startswith("__NEO_TURTLE__:"):
                cmd = parse_turtle_output_line(stripped)
                if cmd:
                    self._bus.draw_command.emit(cmd)
            elif stripped.startswith("__NEO_ROBOT__:"):
                cmd = parse_robot_output_line(stripped)
                if cmd:
                    self._bus.robot_command.emit(cmd)
            else:
                if stripped:
                    self._bus.stdout_received.emit(line)

    def _on_execution_finished(self, result: ExecutionResult) -> None:
        """Handle execution completion + AI feedback on errors."""
        self._bus.execution_finished.emit(result)
        if result.return_code == 0:
            self._output_panel.append_info("\n--- Finished ---\n")
        elif getattr(result, 'was_timeout', False):
            self._output_panel.append_stderr("\n--- Timeout ---\n")
        else:
            self._output_panel.append_stderr(
                f"\n--- Error (code {result.return_code}) ---\n"
            )

        # AI feedback on execution result
        code = self._current_code
        service = self._ai_service

        def ai_task():
            return service.on_execution_result(code, result)

        self._run_ai_task(ai_task)

        # Update progress
        self._bus.progress_updated.emit(self._ai_service.profile)

    def _on_stop(self) -> None:
        if self._execution_worker and self._execution_worker.isRunning():
            self._execution_worker.stop()
            self._execution_worker.wait(2000)
            self._output_panel.append_info("\n--- Stopped ---\n")
        self._toolbar.set_running(False)
        self._status_bar.showMessage("Execution stopped")

    # === AI Assistant ===

    def _on_manual_question(self, question: str) -> None:
        """Handle student's manual question to AI."""
        self._chat_panel.add_user_message(question)
        self._chat_panel.show_thinking()

        code = self._current_code
        analysis = self._last_analysis
        service = self._ai_service

        if analysis is None:
            # No analysis yet, create a minimal one
            from neo_code.core.code_analyzer import analyze_code
            analysis = analyze_code(code)

        def ai_task():
            return service.on_manual_query(question, code, analysis)

        self._run_ai_task(ai_task, show_thinking=False)  # already showing

    def _run_ai_task(self, task, show_thinking: bool = True) -> None:
        """Run an AI task in background thread."""
        # Don't queue if another query is running
        if self._ai_worker and self._ai_worker.isRunning():
            return

        if show_thinking:
            self._chat_panel.show_thinking()

        self._ai_worker = AIQueryWorker(self)
        self._ai_worker.set_task(task)
        self._ai_worker.response_ready.connect(self._on_ai_response)
        self._ai_worker.error_occurred.connect(self._on_ai_error)
        self._ai_worker.start()

    def _on_ai_response(self, response: AIResponse) -> None:
        """Display AI response in chat panel."""
        self._chat_panel.hide_thinking()
        self._chat_panel.display_response(response)

    def _on_ai_error(self, error_msg: str) -> None:
        """Handle AI error."""
        self._chat_panel.hide_thinking()
        logger.error(f"AI error: {error_msg}")

    def _on_language_changed(self, lang: str) -> None:
        """Switch AI response language."""
        self._ai_service.lang = lang
        self._ai_input.set_language(lang)
        lang_name = "Tieng Viet" if lang == "vi" else "English"
        self._chat_panel.add_ai_message(
            f"Language switched to **{lang_name}**."
            if lang == "en" else
            f"Da chuyen sang **{lang_name}**."
        )
        self._status_bar.showMessage(f"Language: {lang_name}")

    # === Level Selector ===

    def _on_level_selector(self) -> None:
        """Open level selector dialog."""
        from neo_code.ui.dialogs.level_selector import LevelSelectorDialog

        dialog = LevelSelectorDialog(current_level=self._current_level, parent=self)
        dialog.level_selected.connect(self._set_level)
        dialog.exec()

    def _set_level(self, level: int) -> None:
        """Set the current difficulty level."""
        self._current_level = level
        self._toolbar.set_level_text(LEVEL_NAMES.get(level, f"Level {level}"))
        self._ai_service.profile.level = level

        level_descriptions = {
            1: "**Level 1 - Kham pha**: Code gan nhu day du, chi can thay 1-2 gia tri.",
            2: "**Level 2 - Lap trinh vien**: Phan quan trong de trong (___), co goi y.",
            3: "**Level 3 - Chuyen gia**: Chi mo ta nhiem vu, tu viet code!",
        }
        desc = level_descriptions.get(level, "")
        self._chat_panel.add_ai_message(
            f"Da chon {desc}\n\nBam **Samples** de bat dau bai hoc!"
        )
        self._status_bar.showMessage(LEVEL_NAMES.get(level, f"Level {level}"))

    # === Samples (Project-based) ===

    def _on_samples(self) -> None:
        """Show projects dropdown menu organized by category."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #313244;
            }
            QMenu::separator {
                height: 1px;
                background: #45475a;
                margin: 4px 8px;
            }
        """)

        categories = get_projects_by_category()
        first_cat = True
        for cat_name, projects in categories.items():
            if not first_cat:
                menu.addSeparator()
            first_cat = False

            category_action = menu.addAction(f"-- {cat_name} --")
            category_action.setEnabled(False)

            for project in projects:
                action = menu.addAction(f"  {project.title}")
                action.setToolTip(project.description)
                action.setData(project.id)

        action = menu.exec(self._toolbar.mapToGlobal(
            self._toolbar.rect().bottomLeft()
        ))
        if action and action.data():
            self._load_project(action.data())

    def _load_project(self, project_id: str) -> None:
        """Load a project at the current difficulty level."""
        from neo_code.education.projects import get_project_by_id

        project = get_project_by_id(project_id)
        if not project:
            return

        level = self._current_level
        level_data = project.levels.get(level)
        if not level_data:
            # Fallback to solution if level not available
            code = project.solution
        else:
            code = level_data.code

        self._editor.set_code(code)
        self._editor.current_file = None
        self._output_panel.clear()
        self._turtle_canvas.reset_turtle()
        self._robot_arena.reset_arena()
        self._status_bar.showMessage(
            f"Loaded: {project.title} ({LEVEL_NAMES.get(level, '')})"
        )

        # Auto-load field for robot projects
        field_id = getattr(project, 'field_id', '')
        if field_id:
            self._current_field_id = field_id
            self._robot_arena.set_field(field_id)
            self._bottom_tabs.setCurrentWidget(self._robot_arena)

        # Show task description in AI chat panel
        task_msg = f"**{project.title}**\n\n"
        task_msg += f"*Nhiem vu:* {project.description}\n\n"

        if level_data and level_data.hints:
            task_msg += "**Goi y:**\n"
            for hint in level_data.hints:
                task_msg += f"- {hint}\n"
            task_msg += "\n"

        task_msg += f"*Khai niem:* {', '.join(project.concepts)}"

        # Show field info for robot projects
        if field_id:
            field_info = self._build_field_info_message(field_id)
            if field_info:
                task_msg += "\n\n---\n" + field_info

        self._chat_panel.add_ai_message(task_msg)

    def _build_field_info_message(self, field_id: str) -> str:
        """Build a markdown message describing the field layout."""
        from neo_code.education.robot_challenges import get_field_config

        config = get_field_config(field_id)
        if not config:
            return ""

        msg = f"**San: {config.name}** ({int(config.field_width)}x{int(config.field_height)}mm)\n\n"

        # Pieces
        if config.game_pieces:
            msg += "**Vat pham:**\n"
            for p in config.game_pieces:
                label = p.label or p.id
                msg += f"- {label} tai ({int(p.x)}, {int(p.y)}) - {p.value} diem\n"
            msg += "\n"

        # Zones
        if config.scoring_zones:
            msg += "**Zone ghi diem:**\n"
            for z in config.scoring_zones:
                msg += f"- {z.label or z.id} tai ({int(z.x)}, {int(z.y)}) - x{z.multiplier}\n"
            msg += "\n"

        # Obstacles
        if config.obstacles:
            msg += "**Chuong ngai vat:**\n"
            for o in config.obstacles:
                msg += f"- {o.id} tai ({int(o.x)}, {int(o.y)})\n"
            msg += "\n"

        # Missions
        if config.missions:
            mission = config.missions[0]
            msg += f"**Nhiem vu: {mission.name}**\n"
            for obj in mission.objectives:
                msg += f"  {obj.order}. {obj.description}"
                if obj.hint:
                    msg += f" *(goi y: {obj.hint})*"
                msg += "\n"
            msg += "\n"

        # Quick rules
        msg += f"*Thoi gian: {config.match_duration}s | "
        msg += f"Grab range: 300mm | "
        msg += "Bam Run de chay code!*"

        return msg

    # === Accessors ===

    def get_editor(self) -> CodeEditorWidget:
        return self._editor

    def get_chat_panel(self) -> AIChatPanel:
        return self._chat_panel

    def get_turtle_canvas(self) -> TurtleCanvasWidget:
        return self._turtle_canvas

    def get_output_panel(self) -> OutputPanel:
        return self._output_panel
