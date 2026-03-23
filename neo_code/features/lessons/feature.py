from PyQt5.QtWidgets import QWidget

from neo_code.core.extension_interface import IFeature
from neo_code.features.lessons.lesson_panel import LessonPanel


class LessonsFeature(IFeature):
    def __init__(self) -> None:
        super().__init__()
        self._sidebar: QWidget | None = None
        self._canvas: QWidget | None = None

    def activate(self) -> None:
        self._sidebar = LessonPanel()
        self._canvas = None

    def deactivate(self) -> None:
        pass

    def get_canvas_widget(self) -> QWidget | None:
        return self._canvas

    def get_sidebar_widget(self) -> QWidget | None:
        return self._sidebar
