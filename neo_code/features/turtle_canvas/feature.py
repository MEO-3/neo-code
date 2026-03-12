"""
TurtleCanvasFeature — stub.
Full implementation in Phase 2.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from neo_code.core.extension_interface import IExtension


class TurtleCanvasFeature(IExtension):
    def activate(self, event_bus) -> None:
        self._event_bus = event_bus

    def deactivate(self) -> None:
        pass

    def get_canvas_widget(self) -> Gtk.Widget | None:
        placeholder = Gtk.Label(label="Turtle Canvas\n(coming in Phase 2)")
        placeholder.set_hexpand(True)
        placeholder.set_vexpand(True)
        placeholder.add_css_class("dim-label")
        return placeholder

    def get_sidebar_widget(self) -> Gtk.Widget | None:
        return None
