from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt

from neo_code.core.extension_interface import IFeature
from neo_code.theme.colors import colors


class RobotFeature(IFeature):
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
        self.setStyleSheet(f"background-color: {colors.panel_bg};")
        label = QLabel("Rô-bốt", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"color: {colors.text_secondary};")
        self._label = label

    def resizeEvent(self, event) -> None:
        self._label.setGeometry(0, 0, self.width(), self.height())
