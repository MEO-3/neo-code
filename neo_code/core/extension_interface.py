"""
IExtension — abstract base class for all hard-coded (and future dynamic) features.

Hard-coded features in `features/` are instantiated directly in main_window.py.
This interface ensures they remain swappable without changing the shell.
"""

from abc import ABC, abstractmethod

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class IExtension(ABC):

    @abstractmethod
    def activate(self, event_bus) -> None:
        """
        Called once after instantiation.
        Subscribe to events, allocate resources, build internal widgets.
        Receives the event_bus module so the extension does not import it directly.
        """

    @abstractmethod
    def deactivate(self) -> None:
        """
        Called when the feature is being torn down.
        Unsubscribe from all events and release resources.
        """

    @abstractmethod
    def get_canvas_widget(self) -> Gtk.Widget | None:
        """
        Widget to place in the right (canvas) panel.
        Return None if this feature has no canvas view.
        """

    @abstractmethod
    def get_sidebar_widget(self) -> Gtk.Widget | None:
        """
        Widget to place in the left sidebar panel.
        Return None if this feature has no sidebar view.
        """
