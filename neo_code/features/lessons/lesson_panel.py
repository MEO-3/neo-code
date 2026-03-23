from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import pyqtSignal

from neo_code.features.lessons.lesson_sidebar import LessonSidebarPanel
from neo_code.features.lessons.lesson_workspace import LessonWorkspacePanel
from neo_code.features.lessons.loader import load_lesson_pack


class LessonPanel(QWidget):
    back_visibility_changed = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        lesson_pack = load_lesson_pack()
        self._list = LessonSidebarPanel(lesson_pack)
        self._detail = LessonWorkspacePanel()

        self._stack = QStackedWidget()
        self._stack.addWidget(self._list)
        self._stack.addWidget(self._detail)
        self._stack.setCurrentWidget(self._list)

        self._list.lesson_selected.connect(self._on_lesson_selected)
        self._detail.progress_updated.connect(self._on_progress_updated)

        layout.addWidget(self._stack)

    def _on_lesson_selected(self, lesson: dict) -> None:
        self._detail.set_lesson(lesson)
        self._stack.setCurrentWidget(self._detail)
        self.back_visibility_changed.emit(True)

    def _on_progress_updated(self, lesson_id: str, progress) -> None:
        self._list.update_progress(lesson_id, progress)

    def handle_back(self) -> None:
        self._stack.setCurrentWidget(self._list)
        self.back_visibility_changed.emit(False)

    def is_detail_visible(self) -> bool:
        return self._stack.currentWidget() is self._detail
