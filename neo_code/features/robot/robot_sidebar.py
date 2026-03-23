from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from neo_code.theme.colors import colors


class RobotSidebarPanel(QWidget):
    mission_selected = pyqtSignal(object)

    def __init__(self, robot_pack: dict) -> None:
        super().__init__()
        self._robot_pack = robot_pack
        self.setStyleSheet(f"background-color: {colors.panel_bg};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(14)
        self._tree.setSelectionMode(QTreeWidget.SingleSelection)
        self._tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self._tree.setStyleSheet(
            f"background-color: {colors.panel_bg};"
            f"color: {colors.text};"
            "border: none;"
            f"selection-background-color: {colors.surface_alt};"
            f"selection-color: {colors.text};"
            "QTreeWidget::item:selected {"
            f"background-color: {colors.surface_alt};"
            f"color: {colors.text};"
            "}"
        )
        font = QFont()
        font.setPointSize(9)
        self._tree.setFont(font)

        self._build_items()
        self._tree.expandAll()
        self._tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._tree)

    def _build_items(self) -> None:
        for module in self._robot_pack.get("modules", []):
            module_item = QTreeWidgetItem([module.get("title", "")])
            module_item.setFlags(module_item.flags() & ~Qt.ItemIsSelectable)
            for mission in module.get("missions", []):
                mission_item = QTreeWidgetItem([mission.get("title", "")])
                mission_item.setFlags(
                    mission_item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled
                )
                mission_item.setData(0, Qt.UserRole, mission)
                module_item.addChild(mission_item)
            self._tree.addTopLevelItem(module_item)

    def select_first_mission(self) -> None:
        for i in range(self._tree.topLevelItemCount()):
            module_item = self._tree.topLevelItem(i)
            if module_item.childCount() <= 0:
                continue
            mission_item = module_item.child(0)
            self._tree.setCurrentItem(mission_item)
            self._tree.scrollToItem(mission_item)
            self._emit_mission(mission_item)
            return

    def _emit_mission(self, item: QTreeWidgetItem) -> None:
        self._tree.setCurrentItem(item)
        mission = item.data(0, Qt.UserRole)
        if mission:
            self.mission_selected.emit(mission)

    def _on_item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        if item.parent() is None:
            return
        self._emit_mission(item)
