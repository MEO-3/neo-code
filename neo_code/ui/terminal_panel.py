"""
Terminal panel — read-only output console.

Subscribes to:
  STDOUT_RECEIVED  (data: text: str) — appends plain text in white
  STDERR_RECEIVED  (data: text: str) — appends text in red
  EXECUTION_STARTED                  — clears the terminal
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Pango

from neo_code.core import event_bus


class TerminalPanel(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._build_ui()
        self._subscribe()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Label
        header = Gtk.Label(label="Output")
        header.add_css_class("caption")
        header.set_halign(Gtk.Align.START)
        header.set_margin_start(6)
        header.set_margin_top(4)
        self.append(header)

        # Scrolled text view
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self._buffer = Gtk.TextBuffer()
        self._tag_stderr = self._buffer.create_tag("stderr", foreground="#FF6B6B")
        self._tag_stdout = self._buffer.create_tag("stdout", foreground="#E0E0E0")

        self._view = Gtk.TextView.new_with_buffer(self._buffer)
        self._view.set_editable(False)
        self._view.set_cursor_visible(False)
        self._view.set_monospace(True)
        self._view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._view.set_left_margin(6)
        self._view.set_right_margin(6)

        # Dark background
        self._view.add_css_class("terminal-view")

        scroll.set_child(self._view)
        self.append(scroll)

    # ── Subscriptions ─────────────────────────────────────────────────────────

    def _subscribe(self) -> None:
        event_bus.subscribe(event_bus.STDOUT_RECEIVED, self._on_stdout)
        event_bus.subscribe(event_bus.STDERR_RECEIVED, self._on_stderr)
        event_bus.subscribe(event_bus.EXECUTION_STARTED, self._on_execution_started)

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_execution_started(self) -> None:
        GLib.idle_add(self._clear)

    def _on_stdout(self, text: str) -> None:
        GLib.idle_add(self._append, text, self._tag_stdout)

    def _on_stderr(self, text: str) -> None:
        GLib.idle_add(self._append, text, self._tag_stderr)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _clear(self) -> bool:
        self._buffer.set_text("")
        return GLib.SOURCE_REMOVE

    def _append(self, text: str, tag: Gtk.TextTag) -> bool:
        end_iter = self._buffer.get_end_iter()
        self._buffer.insert_with_tags(end_iter, text + "\n", tag)
        # Auto-scroll to bottom
        adj = self._view.get_vadjustment()
        if adj:
            adj.set_value(adj.get_upper() - adj.get_page_size())
        return GLib.SOURCE_REMOVE

    def destroy(self) -> None:
        event_bus.unsubscribe(event_bus.STDOUT_RECEIVED, self._on_stdout)
        event_bus.unsubscribe(event_bus.STDERR_RECEIVED, self._on_stderr)
        event_bus.unsubscribe(event_bus.EXECUTION_STARTED, self._on_execution_started)
