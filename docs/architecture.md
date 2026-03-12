# NEO CODE GTK — Architecture & Folder Structure

## Overview

NEO CODE uses an **Event-Driven Architecture** with hard-coded features. The codebase is split into strict layers that never import downward — the core knows nothing about features, and features never talk to each other directly. All communication goes through the **Event Bus**.

An `IExtension` interface is defined in `core/` so future dynamic extensions can be plugged in without restructuring the shell.

---

## Folder Structure

```
neo-code/
├── pyproject.toml               # Project metadata & dependencies (Python 3.11+)
├── docs/
│   ├── app_context.md           # Product context, hardware constraints, roadmap
│   └── architecture.md          # This file
│
└── neo_code/
    ├── __init__.py
    ├── __main__.py               # Entry point — run with: python -m neo_code
    │
    ├── core/                     # Core shell — zero knowledge of features
    ├── ui/                       # Core GTK4 UI — no feature-specific widgets
    ├── execution/                # Subprocess sandboxing layer
    ├── features/                 # Hard-coded product features
    ├── utils/                    # Shared stateless utilities
    └── data/                     # Bundled non-Python resources
```

---

## Layer-by-Layer Breakdown

### `core/` — The Shell

The foundation of the app. Contains only what every other layer depends on. Has **no imports** from anywhere else inside `neo_code/`.

| File | Purpose |
|------|---------|
| `event_bus.py` | Thin PyPubSub wrapper. Defines all event name constants (`EXECUTION_REQUESTED`, `CANVAS_COMMAND`, `FILE_OPENED`, …) used across the app. |
| `extension_interface.py` | `IExtension` ABC. Defines the contract (`activate`, `deactivate`, `get_canvas_widget`, `get_sidebar_widget`) that all features must implement. Enables future dynamic loading without changing the shell. |
| `file_manager.py` | Open / save / recent-files logic. Fires `FILE_OPENED` and `FILE_SAVED` events. |
| `settings.py` | Reads and writes a JSON settings file. Provides typed accessors. |

---

### `ui/` — Core GTK4 Interface

Builds the window and panel layout. Instantiates hard-coded features directly and wires their widgets into the layout. Imports from `core/` only.

| File | Purpose |
|------|---------|
| `main_window.py` | `Adw.ApplicationWindow`. Creates the top-level paned layout, instantiates all features, and places their widgets in the correct panels. |
| `editor_panel.py` | `GtkSourceView 5` code editor widget. Handles syntax highlighting, line numbers, and fires `CODE_CHANGED` events. |
| `terminal_panel.py` | Read-only output terminal. Subscribes to `STDOUT_RECEIVED` and `STDERR_RECEIVED` events to display subprocess output. |
| `sidebar_panel.py` | Left sidebar shell. Swaps in the `get_sidebar_widget()` from whichever feature is active. |
| `toolbar.py` | `Adw.HeaderBar` with Run / Stop actions. Fires `EXECUTION_REQUESTED` and `EXECUTION_STOP_REQUESTED` events on click. |

---

### `execution/` — Subprocess Sandboxing

Runs student code safely in an isolated process. The GTK UI is never blocked. Imports from `core/` only.

| File | Purpose |
|------|---------|
| `runner.py` | Launches the student code as a Python `subprocess` with a memory cap and timeout. Reads stdout line-by-line and fires `STDOUT_RECEIVED` events. Kills the process on timeout or stop request. |
| `proxy_injector.py` | Before execution, rewrites the code source so `import turtle` is replaced by the injected proxy. This intercepts all turtle calls without the student changing anything. |
| `output_parser.py` | Reads lines from stdout and detects JSON command objects (e.g. `{"cmd": "forward", "args": [100]}`). Fires `CANVAS_COMMAND` events for the active canvas feature to consume. |

#### Execution Flow

```
[Run button]
    │
    ▼
toolbar.py fires EXECUTION_REQUESTED
    │
    ▼
runner.py receives event
  → proxy_injector rewrites student code
  → subprocess launched (timeout + memory cap)
  → stdout lines → output_parser
      → plain text  → STDOUT_RECEIVED  → terminal_panel displays it
      → JSON object → CANVAS_COMMAND   → turtle_canvas renders it (GLib.idle_add)
```

---

### `features/` — Hard-Coded Product Features

Each feature is a self-contained package that implements `IExtension`. Features subscribe to events in `activate()` and clean up in `deactivate()`. Features **never import from each other**.

#### `features/turtle_canvas/`

Renders Turtle Graphics commands sent from the student's subprocess.

| File | Purpose |
|------|---------|
| `feature.py` | Implements `IExtension`. Subscribes to `CANVAS_COMMAND` events. Returns the canvas widget for the right panel. |
| `canvas.py` | `Gtk.DrawingArea` backed by a Cairo surface. Exposes `draw_command(cmd)`. |
| `renderer.py` | Translates JSON command objects (`forward`, `right`, `penup`, `color`, …) into Cairo draw calls on the canvas. |
| `turtle_proxy.py` | The proxy script injected into student code. Overrides the `turtle` module API and outputs JSON to stdout instead of opening a window. |

#### `features/curriculum/`

Manages educational projects and tracks student progress.

| File | Purpose |
|------|---------|
| `feature.py` | Implements `IExtension`. Returns the curriculum panel as the sidebar widget. |
| `curriculum_panel.py` | GTK4 sidebar UI: level selector and project list. Fires `PROJECT_OPENED` events when a project is chosen. |
| `models.py` | Pure Python dataclasses: `Level`, `Project`, `StudentProfile`. No GTK, no DB. |
| `storage.py` | SQLite persistence via Python `sqlite3`. Stores student profiles, completed levels, and error history. |
| `projects/` | Bundled project templates, one folder per level. Each project has a `.py` starter file and a `meta.json` (title, description, hints). |

```
projects/
├── level_1/    ← Beginner: straight lines, basic shapes
├── level_2/    ← Intermediate: loops, patterns
└── level_3/    ← Advanced: functions, complex drawings
```

---

### `utils/` — Shared Stateless Utilities

Pure helper modules. No GTK, no events, no state. Safe to import from any layer.

| File | Purpose |
|------|---------|
| `linter.py` | Runs `PyFlakes` and Python `ast` on the editor content. Returns a list of `LintError` objects. |
| `completer.py` | Wraps `Jedi` to provide autocompletion suggestions at a given cursor position. |

---

### `data/` — Bundled Resources

Non-Python files shipped with the application.

| Folder | Contents |
|--------|---------|
| `icons/` | SVG icons for the toolbar and UI elements. |
| `styles/` | CSS files for Libadwaita theme overrides and custom widget styling. |
| `gschemas/` | GSettings XML schema for any settings that benefit from system-level storage. |

---

## Layering Rules

These rules must not be broken. They keep the app maintainable and RAM-efficient.

```
core/        ←  no internal imports
  ↑
ui/          ←  imports core/ only
execution/   ←  imports core/ only
utils/       ←  imports nothing inside neo_code/
  ↑
features/*   ←  imports core/, execution/, utils/ — never other features
```

> `main_window.py` is the **only** place where features are instantiated and wired together.

---

## IExtension Contract

Defined in `core/extension_interface.py`. Any future dynamically loaded plugin must satisfy this interface.

```python
from abc import ABC, abstractmethod
from gi.repository import Gtk

class IExtension(ABC):

    @abstractmethod
    def activate(self, event_bus) -> None:
        """Subscribe to events, build internal state."""

    @abstractmethod
    def deactivate(self) -> None:
        """Unsubscribe from events, release resources."""

    @abstractmethod
    def get_canvas_widget(self) -> Gtk.Widget | None:
        """Widget to place in the right (canvas) panel. None if not applicable."""

    @abstractmethod
    def get_sidebar_widget(self) -> Gtk.Widget | None:
        """Widget to place in the left sidebar. None if not applicable."""
```

---

## Phase Roadmap Mapping

| Phase | Description | Folders |
|-------|-------------|---------|
| **1** | Core IDE Foundation | `core/`, `ui/`, `execution/` |
| **2** | Turtle Visual Output | `features/turtle_canvas/` |
| **3** | Curriculum & Student Profiles | `features/curriculum/` + SQLite |
| **4** | Future Extensions | New packages implementing `IExtension` |
