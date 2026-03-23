from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import pyqtSignal

from neo_code.features.robot.loader import load_robot_pack
from neo_code.features.robot.robot_sidebar import RobotSidebarPanel
from neo_code.features.robot.robot_workspace import RobotWorkspacePanel


class RobotPanel(QWidget):
    back_visibility_changed = pyqtSignal(bool)
    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()
    start_requested = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        pack = load_robot_pack()
        self._list = RobotSidebarPanel(pack)
        self._detail = RobotWorkspacePanel()

        self._stack = QStackedWidget()
        self._stack.addWidget(self._list)
        self._stack.addWidget(self._detail)
        self._stack.setCurrentWidget(self._list)

        self._list.mission_selected.connect(self._on_mission_selected)
        self._detail.connect_requested.connect(self.connect_requested.emit)
        self._detail.disconnect_requested.connect(self.disconnect_requested.emit)
        self._detail.start_requested.connect(self.start_requested.emit)

        layout.addWidget(self._stack)
        self._list.select_first_mission()

    def set_status(self, text: str) -> None:
        self._detail.set_status(text)

    def _on_mission_selected(self, mission: dict) -> None:
        self._detail.set_mission(mission)
        self._stack.setCurrentWidget(self._detail)
        self.back_visibility_changed.emit(True)

    def handle_back(self) -> None:
        self._stack.setCurrentWidget(self._list)
        self.back_visibility_changed.emit(False)

    def is_detail_visible(self) -> bool:
        return self._stack.currentWidget() is self._detail
