"""
SettingsDialog — application preferences with version info and update controls.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from neo_code.core.event_bus import event_bus
from neo_code.core.settings import Settings
from neo_code.core.version import get_version
from neo_code.theme.colors import colors


class SettingsDialog(QDialog):
    """Modal settings dialog with version display and update controls."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._settings = Settings()
        self._checker = None

        self.setWindowTitle("Cài đặt")
        self.setMinimumWidth(380)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # ── Version info ───────────────────────────────────────────────
        version_label = QLabel(f"NEO Code  phiên bản {get_version()}")
        version_label.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {colors.text};"
        )
        layout.addWidget(version_label)

        # ── Update section ─────────────────────────────────────────────
        separator = QLabel("")
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {colors.border};")
        layout.addWidget(separator)

        update_header = QLabel("Cập nhật")
        update_header.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {colors.text_secondary};"
        )
        layout.addWidget(update_header)

        self._chk_auto = QCheckBox("Tự động kiểm tra cập nhật khi khởi động")
        self._chk_auto.setChecked(self._settings.auto_check_update)
        self._chk_auto.toggled.connect(self._on_auto_check_toggled)
        layout.addWidget(self._chk_auto)

        check_row = QHBoxLayout()
        self._btn_check = QPushButton("Kiểm tra cập nhật")
        self._btn_check.setStyleSheet(
            f"background-color: {colors.primary}; color: {colors.primary_text}; "
            f"font-weight: bold; border: none; border-radius: 4px; padding: 6px 16px;"
        )
        self._btn_check.clicked.connect(self._on_check_update)
        check_row.addWidget(self._btn_check)

        self._lbl_status = QLabel("")
        self._lbl_status.setStyleSheet(f"color: {colors.text_secondary};")
        check_row.addWidget(self._lbl_status, stretch=1)
        layout.addLayout(check_row)

        layout.addStretch()

        # ── Close button ───────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    # ── Handlers ───────────────────────────────────────────────────────

    def _on_auto_check_toggled(self, checked: bool) -> None:
        self._settings.auto_check_update = checked
        self._settings.save()

    def _on_check_update(self) -> None:
        self._btn_check.setEnabled(False)
        self._lbl_status.setText("Đang kiểm tra...")
        self._lbl_status.setStyleSheet(f"color: {colors.text_secondary};")

        from neo_code.core.updater import UpdateChecker

        self._checker = UpdateChecker(self)
        self._checker.update_available.connect(self._on_update_found)
        self._checker.finished.connect(self._on_check_finished)
        self._checker.check()

    def _on_update_found(self, version: str, notes: str, url: str) -> None:
        self._found_update = True
        self._lbl_status.setText(f"Có phiên bản mới: {version}")
        self._lbl_status.setStyleSheet(f"color: {colors.primary}; font-weight: bold;")
        # Forward to event_bus so toolbar also shows the indicator
        event_bus.update_available.emit(version, notes, url)

    def _on_check_finished(self) -> None:
        self._btn_check.setEnabled(True)
        if not hasattr(self, "_found_update") or not self._found_update:
            self._lbl_status.setText("Bạn đang dùng phiên bản mới nhất.")
            self._lbl_status.setStyleSheet(f"color: {colors.primary};")
        self._found_update = False
