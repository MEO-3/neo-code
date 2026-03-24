from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QPlainTextEdit,
    QPushButton,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

from neo_code.core.event_bus import event_bus
from neo_code.theme.colors import colors


class RobotWorkspacePanel(QWidget):
    start_requested = pyqtSignal(str)
    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._mission: dict | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        self._title = QLabel("🤖 Nhiệm vụ robot")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self._title.setFont(title_font)
        self._title.setStyleSheet(f"color: {colors.text};")
        root.addWidget(self._title)

        self._status = QLabel("Trạng thái: Chưa tìm kiếm board.")
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {colors.text_secondary};")
        root.addWidget(self._status)

        goal_card, self._goal = self._card("🎯 Mục tiêu", "Chọn một nhiệm vụ để bắt đầu.")
        root.addWidget(goal_card)

        api_card, self._api = self._card(
            "🧪 API thingbot-telemetrix",
            "Ví dụ API sẽ xuất hiện tại đây.",
        )
        self._api.setStyleSheet(
            f"color: {colors.text_secondary};"
            "font-family: monospace;"
        )
        root.addWidget(api_card)

        script_card = QFrame()
        script_card.setStyleSheet(
            f"background-color: {colors.surface};"
            f"border: 1px solid {colors.border};"
            "border-radius: 6px;"
        )
        script_layout = QVBoxLayout(script_card)
        script_layout.setContentsMargins(10, 8, 10, 10)
        script_layout.setSpacing(8)

        script_title = QLabel("🧩 Mã mẫu")
        script_title.setStyleSheet(f"color: {colors.text}; font-weight: bold;")
        script_layout.addWidget(script_title)

        self._starter = QPlainTextEdit()
        self._starter.setReadOnly(True)
        self._starter.setMaximumBlockCount(300)
        self._starter.setStyleSheet(
            f"background-color: {colors.editor_bg};"
            f"color: {colors.editor_text};"
            f"border: 1px solid {colors.border};"
            "border-radius: 4px;"
            "font-family: monospace;"
        )
        script_layout.addWidget(self._starter)
        root.addWidget(script_card)

        self._btn_start = QPushButton("Nạp mã mẫu vào Editor")
        self._btn_start.setCursor(Qt.PointingHandCursor)
        self._btn_start.setStyleSheet(
            f"background-color: {colors.run_bg};"
            f"color: {colors.run_text};"
            "border: none;"
            "border-radius: 5px;"
            "padding: 6px 10px;"
            "font-weight: bold;"
        )
        self._btn_start.clicked.connect(self._on_start_clicked)
        root.addWidget(self._btn_start)

        self._btn_connect = QPushButton("Tìm board USB")
        self._btn_connect.setCursor(Qt.PointingHandCursor)
        self._btn_connect.setToolTip(
            "Quét cổng serial để tìm ThingBot.\n"
            "Board sẽ được kết nối khi bạn nhấn Run."
        )
        self._btn_connect.setStyleSheet(
            f"background-color: {colors.surface_alt};"
            f"color: {colors.text};"
            f"border: 1px solid {colors.border};"
            "border-radius: 5px;"
            "padding: 6px 10px;"
            "font-weight: bold;"
        )
        self._btn_connect.clicked.connect(self.connect_requested.emit)
        root.addWidget(self._btn_connect)

        root.addStretch()

    def set_mission(self, mission: dict) -> None:
        self._mission = mission
        self._title.setText(f"🤖 {mission.get('title', 'Nhiệm vụ')}")
        self._goal.setText(mission.get("goal", ""))
        self._api.setText(mission.get("api_hint", ""))
        self._starter.setPlainText(mission.get("starter_code", ""))

    def set_status(self, text: str) -> None:
        self._status.setText(f"Trạng thái: {text}")

    def _on_start_clicked(self) -> None:
        if not self._mission:
            return
        lesson_like_project = type(
            "RobotProject",
            (),
            {"starter_code": self._mission.get("starter_code", "")},
        )()
        event_bus.project_opened.emit(lesson_like_project)
        self.start_requested.emit(self._mission.get("id", ""))

    def _card(self, title: str, body: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {colors.surface};"
            f"border: 1px solid {colors.border};"
            "border-radius: 6px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {colors.text}; font-weight: bold;")
        layout.addWidget(title_lbl)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(f"color: {colors.text_secondary};")
        layout.addWidget(body_lbl)
        return card, body_lbl
