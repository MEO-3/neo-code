"""
Sidebar panel — left panel shell.

Hosts a stack of sidebar widgets provided by each feature.
The active widget is determined by which tab the user selects.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from neo_code.core.extension_interface import IExtension


class SidebarPanel(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.set_hexpand(False)
        self.set_vexpand(True)
        self.set_size_request(220, -1)

        self._stack = Gtk.Stack()
        self._stack.set_vexpand(True)
        self._stack.set_hexpand(True)
        self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        self._switcher = Gtk.StackSwitcher()
        self._switcher.set_stack(self._stack)
        self._switcher.set_halign(Gtk.Align.CENTER)
        self._switcher.set_margin_top(4)
        self._switcher.set_margin_bottom(4)

        self.append(self._switcher)
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.append(self._stack)

    # ── Public API ────────────────────────────────────────────────────────────

    def add_feature(self, feature: IExtension, name: str, icon_name: str | None = None) -> None:
        """Register a feature's sidebar widget as a named tab."""
        widget = feature.get_sidebar_widget()
        if widget is None:
            return
        self._stack.add_titled(widget, name.lower(), name)
        if icon_name:
            page = self._stack.get_page(widget)
            page.set_icon_name(icon_name)

    def set_active(self, name: str) -> None:
        self._stack.set_visible_child_name(name.lower())
