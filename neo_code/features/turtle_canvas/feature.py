"""
TurtleCanvasFeature — stub (Phase 2 implementation).
"""

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt

from neo_code.core.extension_interface import IFeature


class TurtleCanvasFeature(IFeature):
    def __init__(self) -> None:
        super().__init__()
        self._canvas: QWidget | None = None

    def activate(self) -> None:
        self._canvas = _CanvasPlaceholder()

    def deactivate(self) -> None:
        pass

    def get_canvas_widget(self) -> QWidget | None:
        return self._canvas

    def get_sidebar_widget(self) -> QWidget | None:
        return None


class _CanvasPlaceholder(QWidget):
    def __init__(self) -> None:
        super().__init__()
        label = QLabel("Turtle Canvas\n(Phase 2)", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #6C7086;")
        self.setMinimumWidth(300)
        self.setStyleSheet("background-color: #1E1E2E;")

    def resizeEvent(self, event) -> None:
        # Keep label centered
        for child in self.children():
            if isinstance(child, QLabel):
                child.setGeometry(0, 0, self.width(), self.height())
