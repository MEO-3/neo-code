"""
UpdateDialog — modal dialog showing release notes with Install / Cancel.

Displays download progress and a restart prompt on success.
"""

from __future__ import annotations

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from neo_code.core.updater import UpdateChecker
from neo_code.theme.colors import colors


class UpdateDialog(QDialog):
    """Modal dialog for reviewing and applying an update."""

    def __init__(
        self,
        version: str,
        notes: str,
        download_url: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._download_url = download_url

        self.setWindowTitle("Cập nhật NEO Code")
        self.setMinimumSize(420, 340)
        self.setModal(True)

        self._checker = UpdateChecker(self)

        self._build_ui(version, notes)
        self._connect_signals()

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self, version: str, notes: str) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Header
        header = QLabel(f"Phiên bản mới: {version}")
        header.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {colors.text};")
        layout.addWidget(header)

        # Release notes
        self._notes = QTextEdit()
        self._notes.setReadOnly(True)
        self._notes.setPlainText(notes or "(Không có ghi chú)")
        self._notes.setStyleSheet(
            f"background: {colors.surface}; color: {colors.text}; "
            f"border: 1px solid {colors.border}; border-radius: 4px; padding: 6px;"
        )
        layout.addWidget(self._notes, stretch=1)

        # Progress bar (hidden until download starts)
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setVisible(False)
        self._progress.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid {colors.border};
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background: {colors.surface};
            }}
            QProgressBar::chunk {{
                background-color: {colors.primary};
                border-radius: 3px;
            }}
            """
        )
        layout.addWidget(self._progress)

        # Status label (hidden until needed)
        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._btn_cancel = QPushButton("Bỏ qua")
        self._btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self._btn_cancel)

        self._btn_install = QPushButton("Cập nhật")
        self._btn_install.setStyleSheet(
            f"background-color: {colors.primary}; color: {colors.primary_text}; "
            f"font-weight: bold; border: none; border-radius: 4px; padding: 6px 18px;"
        )
        self._btn_install.clicked.connect(self._on_install)
        btn_layout.addWidget(self._btn_install)

        self._btn_restart = QPushButton("Khởi động lại")
        self._btn_restart.setStyleSheet(
            f"background-color: {colors.primary}; color: {colors.primary_text}; "
            f"font-weight: bold; border: none; border-radius: 4px; padding: 6px 18px;"
        )
        self._btn_restart.setVisible(False)
        self._btn_restart.clicked.connect(self._on_restart)
        btn_layout.addWidget(self._btn_restart)

        layout.addLayout(btn_layout)

    # ── Signals ────────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._checker.download_progress.connect(self._on_progress)
        self._checker.update_finished.connect(self._on_finished)

    # ── Handlers ───────────────────────────────────────────────────────────

    def _on_install(self) -> None:
        self._btn_install.setEnabled(False)
        self._btn_cancel.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._checker.download_and_install(self._download_url)

    def _on_progress(self, pct: int) -> None:
        self._progress.setValue(pct)

    def _on_finished(self, success: bool, message: str) -> None:
        self._status_label.setVisible(True)
        if success:
            self._status_label.setStyleSheet(f"color: {colors.primary}; font-weight: bold;")
            self._status_label.setText(message)
            self._btn_install.setVisible(False)
            self._btn_cancel.setVisible(False)
            self._btn_restart.setVisible(True)
        else:
            self._status_label.setStyleSheet(f"color: {colors.terminal_error};")
            self._status_label.setText(message)
            self._btn_install.setEnabled(True)
            self._btn_cancel.setEnabled(True)

    @staticmethod
    def _on_restart() -> None:
        import os
        os.execv(sys.executable, [sys.executable, "-m", "neo_code"] + sys.argv[1:])
