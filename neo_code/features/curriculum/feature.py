"""
CurriculumFeature — stub (Phase 3 implementation).
"""

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt

from neo_code.core.extension_interface import IFeature


class CurriculumFeature(IFeature):
    def __init__(self) -> None:
        super().__init__()
        self._sidebar: QWidget | None = None

    def activate(self) -> None:
        self._sidebar = _SidebarPlaceholder()

    def deactivate(self) -> None:
        pass

    def get_canvas_widget(self) -> QWidget | None:
        return None

    def get_sidebar_widget(self) -> QWidget | None:
        return self._sidebar


class _SidebarPlaceholder(QWidget):
    def __init__(self) -> None:
        super().__init__()
        label = QLabel("Lessons\n(Phase 3)", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #6C7086;")

    def resizeEvent(self, event) -> None:
        for child in self.children():
            if isinstance(child, QLabel):
                child.setGeometry(0, 0, self.width(), self.height())
