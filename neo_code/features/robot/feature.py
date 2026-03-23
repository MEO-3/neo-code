from PyQt5.QtWidgets import QWidget

from neo_code.core.extension_interface import IFeature
from neo_code.features.robot.robot_panel import RobotPanel


class RobotFeature(IFeature):
    def __init__(self) -> None:
        super().__init__()
        self._sidebar: RobotPanel | None = None

    def activate(self) -> None:
        self._sidebar = RobotPanel()

    def deactivate(self) -> None:
        pass

    def get_canvas_widget(self) -> QWidget | None:
        return None

    def get_sidebar_widget(self) -> QWidget | None:
        return self._sidebar
