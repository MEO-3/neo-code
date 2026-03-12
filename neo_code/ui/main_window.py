"""
Main window — Adw.ApplicationWindow.

Layout:
  ┌────────────────────────────────────────────────────┐
  │  Adw.HeaderBar (Toolbar)                           │
  ├──────────┬─────────────────────────┬───────────────┤
  │ Sidebar  │      Editor             │    Canvas     │
  │ Panel    │      (GtkSourceView)    │    (Feature)  │
  │          ├─────────────────────────┤               │
  │          │      Terminal           │               │
  └──────────┴─────────────────────────┴───────────────┘

Hard-coded features are instantiated here and their widgets placed into layout.
File-open / save dialogs are also managed here (need a window reference).
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from neo_code.core import event_bus
from neo_code.core.file_manager import FileManager
from neo_code.core.settings import Settings
from neo_code.ui.toolbar import Toolbar
from neo_code.ui.editor_panel import EditorPanel
from neo_code.ui.terminal_panel import TerminalPanel
from neo_code.ui.sidebar_panel import SidebarPanel


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app: Adw.Application) -> None:
        super().__init__(application=app)

        self._settings = Settings()
        self._file_manager = FileManager()

        self.set_title("NEO CODE")
        self.set_default_size(1280, 800)

        self._build_ui()
        self._load_features()
        self._subscribe()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # ── Toolbar (header bar) ───────────────────────────────────────────
        self._toolbar = Toolbar(get_code_fn=self._get_editor_code)
        self._toolbar.set_title_widget(Gtk.Label(label="NEO CODE"))
        root_box.append(self._toolbar)

        # ── Three-pane body ───────────────────────────────────────────────
        # Outer paned: sidebar | (editor+terminal+canvas)
        outer_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        outer_paned.set_vexpand(True)
        outer_paned.set_wide_handle(True)

        # Sidebar
        self._sidebar = SidebarPanel()
        outer_paned.set_start_child(self._sidebar)
        outer_paned.set_resize_start_child(False)
        outer_paned.set_shrink_start_child(False)

        # Inner paned: (editor+terminal) | canvas
        inner_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        inner_paned.set_hexpand(True)
        inner_paned.set_wide_handle(True)

        # Editor + Terminal stacked vertically
        editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        editor_box.set_hexpand(True)
        editor_box.set_vexpand(True)

        self._editor = EditorPanel(self._settings)
        self._editor.set_vexpand(True)

        self._terminal = TerminalPanel()
        self._terminal.set_size_request(-1, 160)

        editor_terminal_paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        editor_terminal_paned.set_vexpand(True)
        editor_terminal_paned.set_wide_handle(True)
        editor_terminal_paned.set_start_child(self._editor)
        editor_terminal_paned.set_end_child(self._terminal)
        editor_terminal_paned.set_resize_end_child(False)
        editor_terminal_paned.set_shrink_end_child(False)

        inner_paned.set_start_child(editor_terminal_paned)
        inner_paned.set_resize_start_child(True)

        # Canvas placeholder — replaced by feature widget in _load_features()
        self._canvas_placeholder = Gtk.Box()
        self._canvas_placeholder.set_hexpand(True)
        self._canvas_placeholder.set_vexpand(True)
        self._canvas_placeholder.set_size_request(300, -1)
        inner_paned.set_end_child(self._canvas_placeholder)
        inner_paned.set_resize_end_child(False)
        inner_paned.set_shrink_end_child(False)

        self._inner_paned = inner_paned
        outer_paned.set_end_child(inner_paned)

        root_box.append(outer_paned)
        self.set_content(root_box)

    # ── Feature wiring ────────────────────────────────────────────────────────

    def _load_features(self) -> None:
        """Instantiate and wire all hard-coded features."""
        from neo_code.features.turtle_canvas.feature import TurtleCanvasFeature
        from neo_code.features.curriculum.feature import CurriculumFeature

        self._turtle_feature = TurtleCanvasFeature()
        self._turtle_feature.activate(event_bus)

        self._curriculum_feature = CurriculumFeature()
        self._curriculum_feature.activate(event_bus)

        # Canvas widget (right panel) — turtle canvas
        canvas_widget = self._turtle_feature.get_canvas_widget()
        if canvas_widget:
            self._inner_paned.set_end_child(canvas_widget)

        # Sidebar tabs
        self._sidebar.add_feature(self._curriculum_feature, "Lessons", "open-book-symbolic")

    # ── Subscriptions ─────────────────────────────────────────────────────────

    def _subscribe(self) -> None:
        event_bus.subscribe("ui.open_file_dialog_requested", self._on_open_dialog)
        event_bus.subscribe("ui.save_file_dialog_requested", self._on_save_dialog)
        event_bus.subscribe(event_bus.FILE_SAVED, self._on_file_saved)
        event_bus.subscribe(event_bus.FILE_OPENED, self._on_file_opened)
        event_bus.subscribe(event_bus.FILE_NEW, self._on_file_new)

    # ── File dialog helpers ───────────────────────────────────────────────────

    def _on_open_dialog(self) -> None:
        dialog = Gtk.FileDialog()
        dialog.set_title("Open Python File")
        f = Gtk.FileFilter()
        f.set_name("Python files")
        f.add_pattern("*.py")
        filters = Gio_ListStore_of_filters([f])
        dialog.set_filters(filters)
        dialog.open(self, None, self._open_dialog_cb)

    def _open_dialog_cb(self, dialog, result) -> None:
        try:
            file = dialog.open_finish(result)
            if file:
                self._file_manager.open_file(file.get_path())
        except Exception:
            pass

    def _on_save_dialog(self) -> None:
        if self._file_manager.has_file:
            self._file_manager.save_file(self._get_editor_code())
        else:
            self._show_save_as_dialog()

    def _show_save_as_dialog(self) -> None:
        dialog = Gtk.FileDialog()
        dialog.set_title("Save Python File")
        dialog.set_initial_name("main.py")
        dialog.save(self, None, self._save_dialog_cb)

    def _save_dialog_cb(self, dialog, result) -> None:
        try:
            file = dialog.save_finish(result)
            if file:
                self._file_manager.save_file(self._get_editor_code(), file.get_path())
        except Exception:
            pass

    def _on_file_saved(self, path: str) -> None:
        GLib.idle_add(self.set_title, f"NEO CODE — {path.split('/')[-1]}")

    def _on_file_opened(self, path: str, content: str) -> None:
        GLib.idle_add(self.set_title, f"NEO CODE — {path.split('/')[-1]}")

    def _on_file_new(self) -> None:
        GLib.idle_add(self.set_title, "NEO CODE — Untitled")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_editor_code(self) -> str:
        return self._editor.get_code()

    def destroy(self) -> None:
        self._turtle_feature.deactivate()
        self._curriculum_feature.deactivate()
        self._toolbar.destroy()
        self._editor.destroy()
        self._terminal.destroy()
        super().destroy()


# ── Gio.ListStore helper ───────────────────────────────────────────────────────

def Gio_ListStore_of_filters(filters: list) -> object:
    """Build a Gio.ListStore[Gtk.FileFilter] from a plain list."""
    import gi
    gi.require_version("Gio", "2.0")
    from gi.repository import Gio
    store = Gio.ListStore.new(Gtk.FileFilter)
    for f in filters:
        store.append(f)
    return store
