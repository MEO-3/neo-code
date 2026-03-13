# NEO CODE — Architecture & Folder Structure

## Overview

NEO CODE is an **educational Python IDE** for STEM/Robotics students (ages 6–12) built with **PyQt5**. It uses an **Event-Driven Architecture** with hard-coded features. Layers communicate only through a central `EventBus` — components never import each other directly.

An `IFeature` interface is defined in `core/` so future features can be plugged in without restructuring the shell.

---

## Tech Stack

| Concern | Library / Tool | Why |
|---------|---------------|-----|
| GUI framework | **PyQt5 ≥ 5.15** | Stable on ARM via `apt`; pure pip install on x86; cross-platform |
| Syntax highlighting | `QSyntaxHighlighter` (built-in) | No extra deps; handles Python keywords, strings, comments |
| Code execution | `QProcess` (built-in) | Non-blocking subprocess with stdout/stderr signals; no threading needed |
| REPL execution | `QProcess` (`python3 -u -i`) | Persistent interactive process; stdin written via `QProcess.write()` |
| Autocompletion | **Jedi ≥ 0.19** | Lightweight, local, works offline |
| Linting | **pyflakes ≥ 3.2** + `ast` | Fast, zero config, finds undefined names and syntax errors |
| Persistence | Python `sqlite3` (stdlib) | Student profiles, progress, no extra deps |
| Build & packaging | **hatchling** | `pyproject.toml`-native, produces wheel |
| Entry point | `neo-code` CLI → `neo_code.__main__:main` | Installed via `pip install -e .` |

### Python requirement

Python **3.11+**

---

## Folder Structure

```
neo-code/
├── pyproject.toml               # Project metadata & build config
├── docs/
│   ├── app_context.md           # Product context, hardware constraints, roadmap
│   └── architecture.md          # This file
│
└── neo_code/
    ├── __init__.py
    ├── __main__.py               # Entry point: python -m neo_code  or  neo-code
    ├── app.py                    # NeoCodeApp(QApplication) — palette, style, bootstrap
    │
    ├── core/                     # Shell layer — no imports from any other neo_code package
    │   ├── event_bus.py          # EventBus singleton (typed pyqtSignals)
    │   ├── extension_interface.py # IFeature(QObject) ABC
    │   ├── file_manager.py       # Open / save / new file logic
    │   └── settings.py           # JSON settings read/write
    │
    ├── theme/                    # Global visual tokens
    │   └── colors.py             # Frozen _Palette dataclass + `colors` singleton
    │
    ├── ui/                       # PyQt5 window & panel widgets — imports core/ only
    │   ├── main_window.py        # QMainWindow: layout, feature wiring, file dialogs
    │   ├── toolbar.py            # QToolBar: Run / Stop / New / Open / Save / REPL actions
    │   ├── editor_panel.py       # QPlainTextEdit + PythonHighlighter + line-number gutter
    │   ├── terminal_panel.py     # Output panel: header bar + collapsible QPlainTextEdit
    │   ├── repl_panel.py         # Live Python REPL: output view + input row + QProcess
    │   └── sidebar_panel.py      # VS Code-style activity bar + collapsible content panel
    │
    ├── execution/                # Code runner layer — imports core/ only
    │   └── runner.py             # QProcess executor: 30 s timeout, auto-cleanup
    │
    ├── features/                 # Hard-coded product features — import core/ + utils/ only
    │   └── curriculum/           # Lesson browser & student progress (stub)
    │       └── feature.py        # CurriculumFeature(IFeature) — sidebar placeholder
    │
    └── utils/                    # Stateless helpers — no events, no Qt widgets
        ├── linter.py             # PyFlakes + ast → list[LintError]  (stub)
        └── completer.py          # Jedi completions at cursor position  (stub)
```

---

## Layer-by-Layer Breakdown

### `core/` — The Shell

Foundation of the app. **No imports from any other `neo_code` package.**

| File | Purpose |
|------|---------|
| `event_bus.py` | `EventBus(QObject)` singleton with typed `pyqtSignal`s. All cross-component communication goes here. |
| `extension_interface.py` | `IFeature(QObject)` ABC. Defines the contract: `activate()`, `deactivate()`, `get_sidebar_widget()`. |
| `file_manager.py` | Open / save / new file logic. Emits `file_opened`, `file_saved`, `file_new` on the event bus. |
| `settings.py` | JSON settings stored in `~/.config/neo-code/settings.json`. Typed accessors for font size, last open directory, etc. |

#### EventBus signals

```python
# File lifecycle
file_new            = pyqtSignal()
file_opened         = pyqtSignal(str, str)       # (path, content)
file_saved          = pyqtSignal(str)             # (path,)

# Editor
code_changed        = pyqtSignal(str)             # (code,)  debounced 300 ms

# Execution
execution_requested        = pyqtSignal(str)      # (code,)
execution_stop_requested   = pyqtSignal()
execution_started          = pyqtSignal()
execution_finished         = pyqtSignal(int)      # (exit_code,)
repl_mode_changed          = pyqtSignal(bool)     # True = REPL active

# Subprocess output
stdout_received     = pyqtSignal(str)
stderr_received     = pyqtSignal(str)

# Curriculum
project_opened      = pyqtSignal(object)          # (Project,)

# UI dialogs
open_file_dialog_requested = pyqtSignal()
save_file_dialog_requested = pyqtSignal()
```

---

### `theme/` — Visual Tokens

Single source of truth for all colors. Never hardcode hex strings in widgets.

```python
from neo_code.theme.colors import colors

widget.setStyleSheet(f"background: {colors.primary};")
```

| Token group | Examples |
|-------------|---------|
| Brand | `primary` (#32A852 green), `primary_hover`, `primary_dim`, `primary_text` |
| Background | `background` (#FFFFFF), `surface`, `surface_alt`, `border` |
| Text | `text`, `text_secondary`, `text_disabled` |
| Editor | `editor_bg`, `editor_line_hl`, `editor_selection` |
| Terminal | `terminal_bg` (dark), `terminal_text`, `terminal_error` |
| Syntax | `syn_keyword`, `syn_string`, `syn_number`, `syn_comment`, `syn_decorator` |
| Activity bar | `activity_bar_bg`, `activity_bar_active`, `activity_bar_icon` |
| Toolbar | `toolbar_bg`, `toolbar_border` |
| Buttons | `run_bg/run_text`, `stop_bg/stop_text` |

---

### `ui/` — PyQt5 Interface

Builds the window and panel layout. Imports from `core/` and `theme/` only.

| File | Purpose |
|------|---------|
| `main_window.py` | `QMainWindow`. Creates `QSplitter` layout, instantiates features in `_load_features()`, wires file dialogs, handles REPL panel swap on `repl_mode_changed`. |
| `toolbar.py` | `QToolBar` with Run (F5) / Stop (F6) / New / Open / Save, plus expanding spacer and checkable ⚡ REPL (F9) pinned to the far right. |
| `editor_panel.py` | `QPlainTextEdit` + `PythonHighlighter(QSyntaxHighlighter)` + `_LineNumberArea` gutter. 300 ms debounced `code_changed` signal. |
| `terminal_panel.py` | `TerminalPanel(QWidget)`: always-visible "Output" header with a ▾/▸ toggle + collapsible `_OutputView(QPlainTextEdit)`. |
| `repl_panel.py` | `ReplPanel(QWidget)`: output view (read-only) + `>>> ` input row. Manages a `python3 -u -i` `QProcess`; starts on `showEvent`, kills on `hideEvent`. Strips OSC/ANSI escape codes and Python's interactive prompts from stderr. |
| `sidebar_panel.py` | VS Code-style: 56 px `_ActivityBar` strip + 240 px collapsible `_ContentPanel`. Click active button again to collapse. |

#### Window layout

```
┌─────────────────────────────────────────────────────────────────┐
│  QToolBar  [New] [Open] [Save] | [▶ Run] [■ Stop] ──── [⚡ REPL] │
├────┬────────────┬───────────────────────────────────────────────┤
│ 56 │  Content   │  EditorPanel          (hidden in REPL mode)   │
│ px │  Panel     │  + line-number gutter                         │
│Act.│  (240 px,  │  ReplPanel            (hidden in script mode) │
│Bar │  toggle)   │  ┌─ output view (read-only) ───────────────┐  │
│    │            │  ├─────────────────────────────────────────┤  │
│    │            │  │ >>>  [input line                  ] [↵] │  │
│    │            │  └─────────────────────────────────────────┘  │
│    │            ├───────────────────────────────────────────────┤
│    │            │  TerminalPanel        (hidden in REPL mode)   │
│    │            │  ┌─ Output ──────────────────────── [▾] ───┐  │
│    │            │  │  _OutputView (collapsible)              │  │
└────┴────────────┴──┴────────────────────────────────────────┴──┘
```

#### REPL panel swap

`repl_mode_changed(True)` → editor hidden, ReplPanel shown, TerminalPanel hidden.
`repl_mode_changed(False)` → editor + TerminalPanel restored, ReplPanel hidden (process killed).

---

### `execution/` — Code Runner

Runs student code in a sandboxed `QProcess`. Never blocks the UI. Imports `core/` only.

| File | Purpose |
|------|---------|
| `runner.py` | Listens to `execution_requested`. Writes code to a temp file, launches `QProcess`, reads stdout/stderr. 30 s hard timeout via `QTimer`. Emits `execution_started/finished`. |

#### Execution flow

```
[Run button]  →  execution_requested(code)
                       │
                 runner.py receives
                   → writes temp .py file
                   → QProcess.start("python3", [temp_file])
                   → stdout  →  stdout_received  →  TerminalPanel
                   → stderr  →  stderr_received  →  TerminalPanel
                   → QTimer 30 s  →  process.kill()
                   → process done →  execution_finished(exit_code)
```

---

### `features/` — Hard-Coded Product Features

Each feature is a self-contained package that implements `IFeature`. Features **never import each other**.

#### `IFeature` contract

```python
class IFeature(QObject):

    @abstractmethod
    def activate(self) -> None:
        """Connect to EventBus signals, allocate resources."""

    @abstractmethod
    def deactivate(self) -> None:
        """Disconnect all signals and release resources."""

    @abstractmethod
    def get_sidebar_widget(self) -> QWidget | None:
        """Widget for the sidebar panel. None if not applicable."""
```

#### `features/curriculum/` *(stub)*

Manages educational projects and tracks student progress.

| File | Status | Purpose |
|------|--------|---------|
| `feature.py` | stub | `CurriculumFeature(IFeature)` — sidebar placeholder widget wired into activity bar |
| `curriculum_panel.py` | planned | `QTreeWidget`-based level/project browser; emits `project_opened` |
| `models.py` | planned | Dataclasses: `Level`, `Project`, `StudentProfile` |
| `storage.py` | planned | SQLite persistence: profiles, completed levels, error history |
| `projects/` | planned | Bundled `.py` starter files + `meta.json` per project |

---

### `utils/` — Shared Stateless Utilities

No Qt widgets, no events, no state. Safe to import from any layer.

| File | Status | Purpose |
|------|--------|---------|
| `linter.py` | stub | `PyFlakes` + `ast` → `list[LintError]` |
| `completer.py` | stub | Jedi completions at `(code, line, col)` cursor position |

---

## Layering Rules

```
theme/       ←  no internal imports
core/        ←  no internal imports
  ↑
ui/          ←  imports core/ + theme/ only
execution/   ←  imports core/ only
utils/       ←  imports nothing inside neo_code/
  ↑
features/*   ←  imports core/ + execution/ + utils/ + theme/ — never other features
```

> `main_window._load_features()` is the **only** place features are instantiated and wired into the layout.

---

## Phase Roadmap

| Phase | Status | Description | Primary folders |
|-------|--------|-------------|-----------------|
| **1** | ✅ Done | PyQt5 IDE foundation: editor, terminal, toolbar, activity bar sidebar, theme, event bus, execution runner | `core/`, `ui/`, `execution/`, `theme/` |
| **2** | ✅ Done | REPL mode: interactive Python console, escape-code filtering, toolbar integration | `ui/repl_panel.py`, `core/event_bus.py`, `ui/toolbar.py` |
| **3** | 🔲 Planned | Curriculum & student profiles: lesson browser, SQLite progress tracking | `features/curriculum/` |
| **4** | 🔲 Future | Dynamic extensions via `IFeature` | New packages under `features/` |
