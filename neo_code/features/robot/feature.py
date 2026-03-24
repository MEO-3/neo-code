from PyQt5.QtWidgets import QWidget

from neo_code.core.extension_interface import IFeature
from neo_code.features.robot.robot_connection import find_serial_ports
from neo_code.features.robot.robot_panel import RobotPanel


class RobotFeature(IFeature):
    def __init__(self) -> None:
        super().__init__()
        self._sidebar: RobotPanel | None = None

    def activate(self) -> None:
        self._sidebar = RobotPanel()
        self._sidebar.connect_requested.connect(self._on_connect)
        self._sidebar.disconnect_requested.connect(self._on_disconnect)

    def deactivate(self) -> None:
        pass

    def get_canvas_widget(self) -> QWidget | None:
        return None

    def get_sidebar_widget(self) -> QWidget | None:
        return self._sidebar

    def _on_connect(self) -> None:
        if self._sidebar is None:
            return
        self._sidebar.set_status("Đang tìm board...")
        ports = find_serial_ports()
        if ports:
            port_list = ", ".join(ports)
            self._sidebar.set_status(
                f"✅ Board: {port_list} — Nhấn Run để chạy code!"
            )
        else:
            self._sidebar.set_status(
                "❌ Không tìm thấy board. Kiểm tra cáp USB và thử lại."
            )

    def _on_disconnect(self) -> None:
        if self._sidebar is None:
            return
        self._sidebar.set_status("Đã ngắt kết nối.")
