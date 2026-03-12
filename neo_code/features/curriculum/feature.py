"""
CurriculumFeature — stub.
Full implementation in Phase 3.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from neo_code.core.extension_interface import IExtension


class CurriculumFeature(IExtension):
    def activate(self, event_bus) -> None:
        self._event_bus = event_bus

    def deactivate(self) -> None:
        pass

    def get_canvas_widget(self) -> Gtk.Widget | None:
        return None

    def get_sidebar_widget(self) -> Gtk.Widget | None:
        placeholder = Gtk.Label(label="Lessons\n(coming in Phase 3)")
        placeholder.set_vexpand(True)
        placeholder.set_halign(Gtk.Align.CENTER)
        placeholder.set_valign(Gtk.Align.CENTER)
        placeholder.add_css_class("dim-label")
        return placeholder
