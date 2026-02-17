"""Editor toolbar with Run, Stop, Save, Open, New buttons."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QToolBar, QToolButton, QWidget


class EditorToolbar(QToolBar):
    """Toolbar for code editing actions."""

    run_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    new_clicked = pyqtSignal()
    open_clicked = pyqtSignal()
    save_clicked = pyqtSignal()
    phase_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Editor Toolbar", parent)
        self.setMovable(False)
        self._setup_buttons()

    def _setup_buttons(self) -> None:
        # New File
        self._new_btn = self._make_button("New", "newButton")
        self._new_btn.clicked.connect(self.new_clicked)
        self.addWidget(self._new_btn)

        # Open File
        self._open_btn = self._make_button("Open", "openButton")
        self._open_btn.clicked.connect(self.open_clicked)
        self.addWidget(self._open_btn)

        # Save File
        self._save_btn = self._make_button("Save", "saveButton")
        self._save_btn.clicked.connect(self.save_clicked)
        self.addWidget(self._save_btn)

        self.addSeparator()

        # Run
        self._run_btn = self._make_button("Run", "runButton")
        self._run_btn.clicked.connect(self.run_clicked)
        self.addWidget(self._run_btn)

        # Stop
        self._stop_btn = self._make_button("Stop", "stopButton")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self.stop_clicked)
        self.addWidget(self._stop_btn)

        self.addSeparator()

        # Phase selector
        self._phase_btn = self._make_button("Phase 1: Turtle", "phaseButton")
        self._phase_btn.clicked.connect(self.phase_clicked)
        self.addWidget(self._phase_btn)

    def _make_button(self, text: str, object_name: str) -> QToolButton:
        btn = QToolButton(self)
        btn.setText(text)
        btn.setObjectName(object_name)
        return btn

    def set_running(self, running: bool) -> None:
        """Update button states based on execution status."""
        self._run_btn.setEnabled(not running)
        self._stop_btn.setEnabled(running)

    def set_phase_text(self, text: str) -> None:
        """Update the phase button text."""
        self._phase_btn.setText(text)
