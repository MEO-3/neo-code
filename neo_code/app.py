"""
NEO CODE GTK — Gtk.Application bootstrap.
"""

import importlib.resources
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from neo_code.ui.main_window import MainWindow

_CSS_PATH = Path(__file__).parent / "data" / "styles" / "app.css"


class NeoCodeApp(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id="io.github.neocode")

    def do_startup(self) -> None:
        Adw.Application.do_startup(self)
        self._load_css()

    def do_activate(self) -> None:
        win = self.get_active_window()
        if win is None:
            win = MainWindow(app=self)
        win.present()

    def _load_css(self) -> None:
        provider = Gtk.CssProvider()
        if _CSS_PATH.exists():
            provider.load_from_path(str(_CSS_PATH))
        Gtk.StyleContext.add_provider_for_display(
            self.get_default_display() if hasattr(self, "get_default_display")
            else Gtk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
