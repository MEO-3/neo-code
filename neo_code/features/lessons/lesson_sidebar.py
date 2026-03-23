from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from neo_code.features.lessons.progress_store import get_progress, LessonProgress
from neo_code.theme.colors import colors


class LessonSidebarPanel(QWidget):
    lesson_selected = pyqtSignal(object)

    _ROLE_TITLE = Qt.UserRole + 1

    def __init__(self, lesson_pack: dict) -> None:
        super().__init__()
        self._lesson_pack = lesson_pack
        self._lesson_items: dict[str, QTreeWidgetItem] = {}
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
            f"border: none;"
            f"selection-background-color: {colors.surface_alt};"
            f"selection-color: {colors.text};"
            f"QTreeWidget::item:selected {{"
            f"background-color: {colors.surface_alt};"
            f"color: {colors.text};"
            f"}}"
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
                base_title = lesson.get("title", "")
                lesson_item = QTreeWidgetItem([base_title])
                lesson_item.setFlags(lesson_item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                lesson_item.setData(0, Qt.UserRole, lesson)
                lesson_item.setData(0, self._ROLE_TITLE, base_title)
                if lesson.get("id"):
                    self._lesson_items[lesson["id"]] = lesson_item
                    progress = get_progress(lesson["id"])
                    self._apply_progress(lesson_item, progress)
                world_item.addChild(lesson_item)
            self._tree.addTopLevelItem(world_item)

    def select_first_lesson(self) -> None:
        for i in range(self._tree.topLevelItemCount()):
            world_item = self._tree.topLevelItem(i)
            if world_item.childCount() > 0:
                lesson_item = world_item.child(0)
                self._tree.setCurrentItem(lesson_item)
                self._tree.scrollToItem(lesson_item)
                self._emit_lesson(lesson_item)
                return

    def select_lesson_by_id(self, lesson_id: str) -> None:
        item = self._lesson_items.get(lesson_id)
        if item is None:
            return
        self._tree.setCurrentItem(item)
        self._tree.scrollToItem(item)
        self._emit_lesson(item)

    def update_progress(self, lesson_id: str, progress: LessonProgress) -> None:
        item = self._lesson_items.get(lesson_id)
        if item is None:
            return
        self._apply_progress(item, progress)

    def _apply_progress(self, item: QTreeWidgetItem, progress: LessonProgress) -> None:
        base_title = item.data(0, self._ROLE_TITLE) or item.text(0)
        suffix = self._format_stars(progress)
        item.setText(0, f"{base_title}  {suffix}" if suffix else base_title)
        if progress.attempts:
            item.setToolTip(0, f"Lượt thử: {progress.attempts} • Sao: {progress.stars}/3")
        else:
            item.setToolTip(0, "")

    @staticmethod
    def _format_stars(progress: LessonProgress) -> str:
        if progress.attempts <= 0 and not progress.completed:
            return ""
        stars = max(0, min(3, progress.stars))
        return "★" * stars + "☆" * (3 - stars)

    def _emit_lesson(self, item: QTreeWidgetItem) -> None:
        self._tree.setCurrentItem(item)
        lesson = item.data(0, Qt.UserRole)
        if lesson:
            self.lesson_selected.emit(lesson)

    def _on_item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        if item.parent() is None:
            return
        self._emit_lesson(item)
