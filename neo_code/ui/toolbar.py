"""
Toolbar — QToolBar with Run / Stop / New / Open / Save actions.

Connects to EventBus signals for execution state changes.
"""

from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction

from neo_code.core.event_bus import event_bus
from neo_code.theme.colors import colors

_TOOLBAR_STYLE = f"""
    QToolBar {{
        background-color: {colors.toolbar_bg};
        border-bottom: 1px solid {colors.toolbar_border};
        spacing: 4px;
        padding: 4px 8px;
    }}
    QToolButton {{
        background: transparent;
        color: {colors.text};
        border: none;
        padding: 4px 10px;
        border-radius: 4px;
    }}
    QToolButton:hover {{
        background-color: {colors.surface_alt};
    }}
    QToolButton[text="▶  Run"] {{
        background-color: {colors.run_bg};
        color: {colors.run_text};
        font-weight: bold;
        border-radius: 4px;
        padding: 4px 14px;
    }}
    QToolButton[text="▶  Run"]:hover {{
        background-color: {colors.run_bg_hover};
    }}
    QToolButton[text="■  Stop"] {{
        background-color: {colors.stop_bg};
        color: {colors.stop_text};
        font-weight: bold;
        border-radius: 4px;
        padding: 4px 14px;
    }}
    QToolButton[text="■  Stop"]:hover {{
        background-color: {colors.stop_bg_hover};
    }}
    QToolButton:disabled {{
        color: {colors.text_disabled};
    }}
"""


class Toolbar(QToolBar):
    def __init__(self, get_code_fn) -> None:
        super().__init__()
        self._get_code = get_code_fn
        self.setMovable(False)
        self._build_actions()
        self._connect_signals()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_actions(self) -> None:
        self.setStyleSheet(_TOOLBAR_STYLE)
        self._act_new = QAction("New", self)
        self._act_new.setShortcut("Ctrl+N")
        self._act_new.triggered.connect(lambda: event_bus.file_new.emit())
        self.addAction(self._act_new)

        self._act_open = QAction("Open", self)
        self._act_open.setShortcut("Ctrl+O")
        self._act_open.triggered.connect(
            lambda: event_bus.open_file_dialog_requested.emit()
        )
        self.addAction(self._act_open)

        self._act_save = QAction("Save", self)
        self._act_save.setShortcut("Ctrl+S")
        self._act_save.triggered.connect(
            lambda: event_bus.save_file_dialog_requested.emit()
        )
        self.addAction(self._act_save)

        self.addSeparator()

        self._act_run = QAction("▶  Run", self)
        self._act_run.setShortcut("F5")
        self._act_run.triggered.connect(self._on_run)
        self.addAction(self._act_run)

        self._act_stop = QAction("■  Stop", self)
        self._act_stop.setShortcut("F6")
        self._act_stop.setEnabled(False)
        self._act_stop.triggered.connect(
            lambda: event_bus.execution_stop_requested.emit()
        )
        self.addAction(self._act_stop)

    # ── Signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        event_bus.execution_started.connect(self._on_execution_started)
        event_bus.execution_finished.connect(self._on_execution_finished)

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_run(self) -> None:
        event_bus.execution_requested.emit(self._get_code())

    def _on_execution_started(self) -> None:
        self._act_run.setEnabled(False)
        self._act_stop.setEnabled(True)

    def _on_execution_finished(self, _exit_code: int) -> None:
        self._act_run.setEnabled(True)
        self._act_stop.setEnabled(False)
