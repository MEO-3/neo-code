"""
Main window — QMainWindow.

Layout:
  ┌──────────────────────────────────────────────────────┐
  │  QToolBar (Toolbar)                                  │
  ├────┬──────────┬───────────────────────────────────── ┤
  │Act.│ Content  │  Editor (QPlainTextEdit)             │
  │Bar │ Panel    │                                      │
  │    │ (toggle) ├──────────────────────────────────────┤
  │    │          │  Terminal (read-only)                │
  └────┴──────────┴──────────────────────────────────────┘

Hard-coded features are instantiated here and their widgets placed into layout.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QFileDialog,
)
from PyQt5.QtCore import Qt, pyqtSlot

from neo_code.core.event_bus import event_bus
from neo_code.core.file_manager import FileManager
from neo_code.core.settings import Settings
from neo_code.ui.toolbar import Toolbar
from neo_code.ui.editor_panel import EditorPanel
from neo_code.ui.terminal_panel import TerminalPanel
from neo_code.ui.sidebar_panel import SidebarPanel
from neo_code.ui.repl_panel import ReplPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._settings = Settings()
        self._file_manager = FileManager()

        self.setWindowTitle("NEO Code")
        self.resize(1280, 800)

        self._build_ui()
        self._load_features()
        self._connect_signals()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # ── Toolbar ───────────────────────────────────────────────────────
        self._editor = EditorPanel(self._settings)
        self._toolbar = Toolbar(get_code_fn=self._editor.get_code)
        self.addToolBar(self._toolbar)

        # ── Central widget ────────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Outer splitter: sidebar | editor+terminal
        outer_splitter = QSplitter(Qt.Horizontal)
        outer_splitter.setHandleWidth(1)

        self._sidebar = SidebarPanel()
        outer_splitter.addWidget(self._sidebar)
        outer_splitter.setCollapsible(0, False)

        # Editor (top) | terminal (bottom)
        self._editor_terminal_splitter = QSplitter(Qt.Vertical)
        self._editor_terminal_splitter.setChildrenCollapsible(False)
        self._editor_terminal_splitter.addWidget(self._editor)

        self._repl = ReplPanel()
        self._repl.hide()
        self._editor_terminal_splitter.insertWidget(0, self._repl)

        self._terminal = TerminalPanel()
        self._editor_terminal_splitter.addWidget(self._terminal)
        self._editor_terminal_splitter.setSizes([0, 600, 160])
        editor_terminal_splitter = self._editor_terminal_splitter

        outer_splitter.addWidget(editor_terminal_splitter)
        outer_splitter.setSizes([56, 1000])
        self._outer_splitter = outer_splitter

        root_layout.addWidget(outer_splitter)

    # ── Feature wiring ────────────────────────────────────────────────────────

    def _load_features(self) -> None:
        from neo_code.features.curriculum.feature import CurriculumFeature

        self._curriculum = CurriculumFeature()
        self._curriculum.activate()

        self._sidebar.add_feature(self._curriculum, key="lessons", icon="📖", label="Lessons")
        self._sidebar.set_active("lessons")

    # ── Signal connections ────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        event_bus.open_file_dialog_requested.connect(self._on_open_dialog)
        event_bus.save_file_dialog_requested.connect(self._on_save_dialog)
        event_bus.file_saved.connect(self._on_file_saved)
        event_bus.file_opened.connect(self._on_file_opened)
        event_bus.file_new.connect(self._on_file_new)
        event_bus.repl_mode_changed.connect(self._on_repl_mode_changed)

    # ── File dialogs ──────────────────────────────────────────────────────────

    @pyqtSlot()
    def _on_open_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Python File",
            self._settings.last_open_dir,
            "Python Files (*.py);;All Files (*)"
        )
        if path:
            self._settings.last_open_dir = str(__import__("pathlib").Path(path).parent)
            self._file_manager.open_file(path)

    @pyqtSlot()
    def _on_save_dialog(self) -> None:
        if self._file_manager.has_file:
            self._file_manager.save_file(self._editor.get_code())
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Python File",
                self._settings.last_open_dir + "/main.py",
                "Python Files (*.py);;All Files (*)"
            )
            if path:
                self._file_manager.save_file(self._editor.get_code(), path)

    @pyqtSlot(str)
    def _on_file_saved(self, path: str) -> None:
        self.setWindowTitle(f"NEO Code — {path.split('/')[-1]}")

    @pyqtSlot(str, str)
    def _on_file_opened(self, path: str, _content: str) -> None:
        self.setWindowTitle(f"NEO Code — {path.split('/')[-1]}")

    @pyqtSlot()
    def _on_file_new(self) -> None:
        self.setWindowTitle("NEO Code — Untitled")

    @pyqtSlot(bool)
    def _on_repl_mode_changed(self, active: bool) -> None:
        self._editor.setVisible(not active)
        self._repl.setVisible(active)
        self._terminal.setVisible(not active)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._settings.save()
        self._curriculum.deactivate()
        super().closeEvent(event)
