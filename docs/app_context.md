# NEO CODE — Application Context

## 1. App Overview

**NEO CODE** is an educational Integrated Development Environment (IDE) designed for STEM and Robotics students (aged 6–12) to learn Python programming through structured, project-based lessons.

The application is built with **PyQt6** to run efficiently on low-resource Armbian devices without requiring system-level package installations.

### Target Hardware Constraints

| Constraint | Value |
|-----------|-------|
| OS | Armbian (Linux) |
| CPU | ARM (e.g. Rockchip RK3566) or x86 AMD (dev machine) |
| Memory | 2 GB RAM |
| Storage | 16 GB eMMC |

**Strategy:** Avoid heavy web frameworks (Electron, web views). Use a pure-Python GUI (`PyQt6`) installable via `pip` with no `apt` dependencies. Defer heavy features to later phases so the baseline IDE stays under ~100 MB RAM.

---

## 2. Technology Stack

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Language | Python 3.11+ | Target audience writes Python; same runtime for app and student code |
| GUI Framework | **PyQt6 ≥ 6.6** | Pure `pip install`; no system packages; cross-platform; Qt Designer available |
| Syntax highlighting | `QSyntaxHighlighter` (built-in Qt) | Zero extra deps; handles Python keywords, strings, comments, decorators |
| Code execution | `QProcess` (built-in Qt) | Non-blocking subprocess with Qt signals; no manual threading |
| Autocompletion | **Jedi ≥ 0.19** | Lightweight, offline, works without a language server |
| Static analysis | **pyflakes ≥ 3.2** + `ast` | Fast, zero-config, offline |
| Persistence | Python `sqlite3` (stdlib) | Student profiles and progress; no extra deps |
| Build & packaging | **hatchling** | `pyproject.toml`-native wheel builder |

---

## 3. Core Architecture

The system uses a **layered, event-driven architecture** with hard-coded features.

### Layers (top → bottom)

```
features/   ← product features (curriculum, turtle canvas)
ui/         ← Qt window & panels
execution/  ← code runner (QProcess)
core/       ← event bus, file manager, settings, IFeature interface
theme/      ← color palette singleton
utils/      ← stateless helpers (linter, completer)
```

Layers only import downward. Features never import each other. All cross-component communication goes through the **Event Bus**.

### Event Bus

`EventBus` is a singleton `QObject` with typed `pyqtSignal`s. Every component connects to and emits signals on this shared object — no component calls another component directly.

```
toolbar  →  execution_requested  →  runner
runner   →  stdout_received      →  terminal_panel
runner   →  canvas_command       →  turtle_canvas  (Phase 2)
toolbar  →  open_file_dialog_requested  →  main_window
```

### Feature Interface (`IFeature`)

Every product feature implements `IFeature(QObject)`:

- `activate()` — connect to EventBus signals, build widgets
- `deactivate()` — disconnect and release resources
- `get_sidebar_widget()` — widget for the activity bar content panel
- `get_canvas_widget()` — widget for the canvas panel (turtle, Phase 2)

Features are instantiated **only** in `main_window._load_features()`. No dynamic loading in Phase 1.

---

## 4. Features

### Currently Active

| Feature | Status | Description |
|---------|--------|-------------|
| **Code Editor** | ✅ Done | `QPlainTextEdit` + Python syntax highlighting + line-number gutter |
| **Output Terminal** | ✅ Done | Read-only console; shows stdout/stderr; collapsible with toggle button |
| **Toolbar** | ✅ Done | Run (F5), Stop (F6), New, Open, Save |
| **Activity Bar Sidebar** | ✅ Done | VS Code-style 56 px icon strip + collapsible 240 px content panel |
| **Theme System** | ✅ Done | Green (#32A852) primary + white background; all tokens in `theme/colors.py` |
| **Curriculum (sidebar)** | 🔲 Stub | Sidebar placeholder wired; full lesson browser planned Phase 3 |

### Planned / Not Yet Implemented

| Feature | Phase | Description |
|---------|-------|-------------|
| **Turtle Canvas** | 2 | `QPainter`-based canvas; proxy intercepts `import turtle`, outputs JSON to stdout |
| **Curriculum engine** | 3 | `QTreeWidget` lesson browser, SQLite student profiles, bundled project templates |
| **Linter feedback** | — | PyFlakes + ast inline error markers in the editor |
| **Autocompletion** | — | Jedi completions on keypress |

### Explicitly Out of Scope (Phase 1–3)

- AI Assistant (Ollama / cloud LLM) — deferred to a future phase; will integrate via `IFeature`
- Hardware / GPIO (`gpiozero`) — deferred; same interface pattern
- Robot Arena — removed from scope

---

## 5. Execution Flow & Sandboxing

Student code runs in an isolated `QProcess` to prevent it from freezing the UI or crashing the system.

1. **Proxy injection** — `proxy_injector.py` prepends a `sys.path` entry so `import turtle` resolves to the bundled proxy instead of the stdlib turtle module. The modified code is written to a `NamedTemporaryFile`.
2. **Process launch** — `runner.py` calls `QProcess.start("python", [temp_file])`. The Qt event loop handles stdout/stderr asynchronously via signals — no manual threads needed.
3. **Output classification** — `output_parser.py` reads each stdout line: plain text → `stdout_received` → terminal; JSON object → `canvas_command` → turtle canvas renderer (Phase 2).
4. **Timeout** — a `QTimer` kills the process after 30 seconds if it has not exited.
5. **Cleanup** — the temp file is deleted and `execution_finished(exit_code)` is emitted.

```
[Run button]
    │  execution_requested(code)
    ▼
runner.py
  → proxy_injector  →  temp .py file
  → QProcess.start()
      stdout  →  output_parser
                  plain text  →  stdout_received  →  TerminalPanel
                  JSON        →  canvas_command   →  TurtleCanvas (Phase 2)
      QTimer 30s  →  process.kill()
      finished    →  execution_finished(exit_code)
```

---

## 6. Development Roadmap

| Phase | Status | Goal |
|-------|--------|------|
| **1 — IDE Foundation** | ✅ Done | PyQt6 window, editor with line numbers, output terminal, toolbar, activity bar sidebar, event bus, QProcess runner, theme system |
| **2 — Visual Output** | 🔲 Planned | Turtle canvas: `QPainter` renderer + turtle proxy injection |
| **3 — Curriculum** | 🔲 Planned | Lesson browser (`QTreeWidget`), bundled project templates, SQLite student profiles and progress tracking |
| **4 — Extensions** | 🔲 Future | AI Assistant and Hardware/GPIO as optional `IFeature` plugins; dynamic loading |

---

## 7. Running the App

```bash
# Create and activate environment
conda create -n neo python=3.11
conda activate neo

# Install dependencies
pip install -e .

# Run
python -m neo_code
# or
neo-code
```
