"""
IFeature — abstract base class for all hard-coded (and future dynamic) features.

Hard-coded features in `features/` are instantiated directly in main_window.py.
This interface keeps them swappable without changing the shell.

Inherits QObject so features can define their own Qt signals if needed.
"""

from abc import abstractmethod

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget


class IFeature(QObject):

    @abstractmethod
    def activate(self) -> None:
        """
        Called once after instantiation.
        Connect to EventBus signals, allocate resources, build internal widgets.
        """

    @abstractmethod
    def deactivate(self) -> None:
        """
        Disconnect all signals and release resources.
        """

    @abstractmethod
    def get_canvas_widget(self) -> QWidget | None:
        """
        Widget for the right (canvas) panel.
        Return None if this feature has no canvas view.
        """

    @abstractmethod
    def get_sidebar_widget(self) -> QWidget | None:
        """
        Widget for the left sidebar panel.
        Return None if this feature has no sidebar view.
        """
