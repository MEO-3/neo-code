"""
Editor panel — GtkSourceView 5 code editor.

Fires:
  CODE_CHANGED  (data: code: str)  — debounced, on every edit

Subscribes to:
  FILE_OPENED   — loads file content into the buffer
  FILE_NEW      — clears the buffer
  PROJECT_OPENED — loads project starter code (forwarded from curriculum)
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("GtkSource", "5")
from gi.repository import Gtk, GtkSource, GLib, Pango

from neo_code.core import event_bus
from neo_code.core.settings import Settings

# Internal event used within the UI layer only
CODE_CHANGED = "code.changed"


class EditorPanel(Gtk.ScrolledWindow):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings
        self._change_timer: int | None = None

        self._build_ui()
        self._subscribe()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Language manager for Python syntax highlighting
        lang_mgr = GtkSource.LanguageManager.get_default()
        python_lang = lang_mgr.get_language("python3")

        # Source buffer
        self._buffer = GtkSource.Buffer()
        if python_lang:
            self._buffer.set_language(python_lang)
        self._buffer.set_highlight_syntax(True)
        self._buffer.set_highlight_matching_brackets(True)
        self._apply_color_scheme()

        # Source view
        self._view = GtkSource.View.new_with_buffer(self._buffer)
        self._view.set_show_line_numbers(True)
        self._view.set_highlight_current_line(True)
        self._view.set_auto_indent(True)
        self._view.set_indent_on_tab(True)
        self._view.set_tab_width(self._settings.tab_width)
        self._view.set_insert_spaces_instead_of_tabs(True)
        self._view.set_smart_backspace(True)
        self._view.set_monospace(True)
        self._apply_font()

        self._buffer.connect("changed", self._on_buffer_changed)
        self.set_child(self._view)

    def _apply_color_scheme(self) -> None:
        scheme_mgr = GtkSource.StyleSchemeManager.get_default()
        scheme_name = "Adwaita-dark" if self._settings.theme == "dark" else "Adwaita"
        scheme = scheme_mgr.get_scheme(scheme_name)
        if scheme:
            self._buffer.set_style_scheme(scheme)

    def _apply_font(self) -> None:
        font_desc = Pango.FontDescription.from_string(
            f"Monospace {self._settings.font_size}"
        )
        self._view.override_font(font_desc)

    # ── Subscriptions ─────────────────────────────────────────────────────────

    def _subscribe(self) -> None:
        event_bus.subscribe(event_bus.FILE_OPENED, self._on_file_opened)
        event_bus.subscribe(event_bus.FILE_NEW, self._on_file_new)
        event_bus.subscribe(event_bus.PROJECT_OPENED, self._on_project_opened)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_code(self) -> str:
        start = self._buffer.get_start_iter()
        end = self._buffer.get_end_iter()
        return self._buffer.get_text(start, end, include_hidden_chars=True)

    def set_code(self, content: str) -> None:
        self._buffer.set_text(content)
        self._buffer.place_cursor(self._buffer.get_start_iter())

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_buffer_changed(self, _buffer) -> None:
        # Debounce: only fire CODE_CHANGED 300 ms after the last keystroke
        if self._change_timer is not None:
            GLib.source_remove(self._change_timer)
        self._change_timer = GLib.timeout_add(300, self._emit_code_changed)

    def _emit_code_changed(self) -> bool:
        self._change_timer = None
        event_bus.publish(CODE_CHANGED, code=self.get_code())
        return GLib.SOURCE_REMOVE

    def _on_file_opened(self, path: str, content: str) -> None:
        self.set_code(content)

    def _on_file_new(self) -> None:
        self.set_code("")

    def _on_project_opened(self, project) -> None:
        if hasattr(project, "starter_code"):
            self.set_code(project.starter_code)

    def destroy(self) -> None:
        event_bus.unsubscribe(event_bus.FILE_OPENED, self._on_file_opened)
        event_bus.unsubscribe(event_bus.FILE_NEW, self._on_file_new)
        event_bus.unsubscribe(event_bus.PROJECT_OPENED, self._on_project_opened)
