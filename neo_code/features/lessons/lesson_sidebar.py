from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from neo_code.theme.colors import colors


class LessonSidebarPanel(QWidget):
    lesson_selected = pyqtSignal(object)

    def __init__(self, lesson_pack: dict) -> None:
        super().__init__()
        self._lesson_pack = lesson_pack
        self.setStyleSheet(f"background-color: {colors.panel_bg};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(14)
        self._tree.setStyleSheet(
            f"background-color: {colors.panel_bg};"
            f"color: {colors.text};"
            f"border: none;"
        )

        font = QFont()
        font.setPointSize(9)
        self._tree.setFont(font)

        self._build_items()
        self._tree.expandAll()
        self._tree.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self._tree)

    def _build_items(self) -> None:
        for world in self._lesson_pack.get("worlds", []):
            world_item = QTreeWidgetItem([world.get("title", "")])
            world_item.setFlags(world_item.flags() & ~Qt.ItemIsSelectable)
            for lesson in world.get("lessons", []):
                lesson_item = QTreeWidgetItem([lesson.get("title", "")])
                lesson_item.setData(0, Qt.UserRole, lesson)
                world_item.addChild(lesson_item)
            self._tree.addTopLevelItem(world_item)

    def select_first_lesson(self) -> None:
        for i in range(self._tree.topLevelItemCount()):
            world_item = self._tree.topLevelItem(i)
            if world_item.childCount() > 0:
                lesson_item = world_item.child(0)
                self._tree.setCurrentItem(lesson_item)
                self._emit_lesson(lesson_item)
                return

    def _emit_lesson(self, item: QTreeWidgetItem) -> None:
        lesson = item.data(0, Qt.UserRole)
        if lesson:
            self.lesson_selected.emit(lesson)

    def _on_item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        if item.parent() is None:
            return
        self._emit_lesson(item)
