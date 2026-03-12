"""
Toolbar — Adw.HeaderBar with Run / Stop actions.

Fires:
  EXECUTION_REQUESTED  (data: code: str)   — when Run is clicked
  EXECUTION_STOP_REQUESTED                 — when Stop is clicked

Subscribes to:
  EXECUTION_STARTED   — disables Run, enables Stop
  EXECUTION_FINISHED  — re-enables Run, disables Stop
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from neo_code.core import event_bus


class Toolbar(Adw.HeaderBar):
    def __init__(self, get_code_fn) -> None:
        super().__init__()
        # Callback that returns the current editor content
        self._get_code = get_code_fn

        self._build_ui()
        self._subscribe()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.set_show_end_title_buttons(True)

        # Run button
        self._btn_run = Gtk.Button(label="▶  Run")
        self._btn_run.add_css_class("suggested-action")
        self._btn_run.connect("clicked", self._on_run)
        self.pack_start(self._btn_run)

        # Stop button
        self._btn_stop = Gtk.Button(label="■  Stop")
        self._btn_stop.add_css_class("destructive-action")
        self._btn_stop.set_sensitive(False)
        self._btn_stop.connect("clicked", self._on_stop)
        self.pack_start(self._btn_stop)

        # New / Open / Save actions on the right
        menu_box = Gtk.Box(spacing=4)

        btn_new = Gtk.Button(label="New")
        btn_new.connect("clicked", lambda _: event_bus.publish(event_bus.FILE_NEW))
        menu_box.append(btn_new)

        self._btn_open = Gtk.Button(label="Open")
        self._btn_open.connect("clicked", self._on_open)
        menu_box.append(self._btn_open)

        self._btn_save = Gtk.Button(label="Save")
        self._btn_save.connect("clicked", self._on_save)
        menu_box.append(self._btn_save)

        self.pack_end(menu_box)

    # ── Event subscriptions ───────────────────────────────────────────────────

    def _subscribe(self) -> None:
        event_bus.subscribe(event_bus.EXECUTION_STARTED, self._on_execution_started)
        event_bus.subscribe(event_bus.EXECUTION_FINISHED, self._on_execution_finished)

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_run(self, _btn) -> None:
        code = self._get_code()
        event_bus.publish(event_bus.EXECUTION_REQUESTED, code=code)

    def _on_stop(self, _btn) -> None:
        event_bus.publish(event_bus.EXECUTION_STOP_REQUESTED)

    def _on_open(self, _btn) -> None:
        # File-open dialog is handled by main_window; just fire a sentinel event.
        event_bus.publish("ui.open_file_dialog_requested")

    def _on_save(self, _btn) -> None:
        event_bus.publish("ui.save_file_dialog_requested")

    def _on_execution_started(self) -> None:
        GLib.idle_add(self._set_running_state, True)

    def _on_execution_finished(self, exit_code: int) -> None:
        GLib.idle_add(self._set_running_state, False)

    def _set_running_state(self, running: bool) -> bool:
        self._btn_run.set_sensitive(not running)
        self._btn_stop.set_sensitive(running)
        return GLib.SOURCE_REMOVE

    def destroy(self) -> None:
        event_bus.unsubscribe(event_bus.EXECUTION_STARTED, self._on_execution_started)
        event_bus.unsubscribe(event_bus.EXECUTION_FINISHED, self._on_execution_finished)
