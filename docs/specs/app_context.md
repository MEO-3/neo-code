# NEO CODE — Application Context

## 1. App Overview

**NEO CODE** is an educational Integrated Development Environment (IDE) designed for STEM and Robotics students (aged 6–12) to learn Python programming through structured, project-based lessons.

The application is built with **PyQt5** to run efficiently on low-resource Armbian devices. On ARM hardware the Qt libraries are installed from the system `apt` repository; on x86 the pip wheel bundles Qt automatically.

### Target Hardware Constraints

| Constraint | Value |
|-----------|-------|
| OS | Armbian (Linux) |
| CPU | ARM (e.g. Rockchip RK3566) or x86 AMD (dev machine) |
| Memory | 2 GB RAM |
| Storage | 16 GB eMMC |

**Strategy:** Avoid heavy web frameworks (Electron, web views). Use a pure-Python GUI (`PyQt5`). On ARM, install Qt via `apt` to avoid the large pip wheel. Defer heavy features to later phases so the baseline IDE stays under ~100 MB RAM.

---

## 2. Technology Stack

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Language | Python 3.11+ | Target audience writes Python; same runtime for app and student code |
| GUI Framework | **PyQt5 ≥ 5.15** | Stable on ARM via `apt`; cross-platform; Qt Designer available |
| Syntax highlighting | `QSyntaxHighlighter` (built-in Qt) | Zero extra deps; handles Python keywords, strings, comments, decorators |
| Code execution | `QProcess` (built-in Qt) | Non-blocking subprocess with Qt signals; no manual threading |
| REPL execution | `QProcess` (`python3 -u -i`) | Persistent interactive process; stdin/stdout/stderr via Qt signals |
| Autocompletion | **Jedi ≥ 0.19** | Lightweight, offline, works without a language server |
| Static analysis | **pyflakes ≥ 3.2** + `ast` | Fast, zero-config, offline |
| Persistence | Python `sqlite3` (stdlib) | Student profiles and progress; no extra deps |
| Build & packaging | **hatchling** | `pyproject.toml`-native wheel builder |

---

## 3. Core Architecture

The system uses a **layered, event-driven architecture** with hard-coded features.

### Layers (top → bottom)

```
features/   ← product features (curriculum)
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
toolbar  →  execution_requested    →  runner
runner   →  stdout_received        →  terminal_panel
toolbar  →  repl_mode_changed      →  main_window, toolbar
toolbar  →  open_file_dialog_requested  →  main_window
```

### Feature Interface (`IFeature`)

Every product feature implements `IFeature(QObject)`:

- `activate()` — connect to EventBus signals, build widgets
- `deactivate()` — disconnect and release resources
- `get_sidebar_widget()` — widget for the activity bar content panel

Features are instantiated **only** in `main_window._load_features()`. No dynamic loading.

---

## 4. Features

### Currently Active

| Feature | Status | Description |
|---------|--------|-------------|
| **Code Editor** | ✅ Done | `QPlainTextEdit` + Python syntax highlighting + line-number gutter |
| **Output Terminal** | ✅ Done | Read-only console; shows stdout/stderr; collapsible with toggle button |
| **REPL Mode** | ✅ Done | Live interactive Python console (`python3 -u -i`); toggled via ⚡ REPL button (F9); replaces editor+terminal while active |
| **Toolbar** | ✅ Done | Run (F5), Stop (F6), New, Open, Save; REPL toggle (F9) pinned to far right |
| **Activity Bar Sidebar** | ✅ Done | VS Code-style 56 px icon strip + collapsible 240 px content panel |
| **Theme System** | ✅ Done | Green (#32A852) primary + white background; all tokens in `theme/colors.py` |
| **Curriculum (sidebar)** | 🔲 Stub | Sidebar placeholder wired; full lesson browser planned |

### Planned / Not Yet Implemented

| Feature | Phase | Description |
|---------|-------|-------------|
| **Curriculum engine** | 3 | `QTreeWidget` lesson browser, SQLite student profiles, bundled project templates |
| **Linter feedback** | — | PyFlakes + ast inline error markers in the editor |
| **Autocompletion** | — | Jedi completions on keypress |

### Explicitly Out of Scope

- Turtle canvas — removed from roadmap
- AI Assistant (Ollama / cloud LLM) — deferred to a future phase
- Hardware / GPIO (`gpiozero`) — deferred
- Robot Arena — removed from scope

---

## 5. Execution Flow & Sandboxing

### Script mode (Run button)

Student code runs in an isolated `QProcess` to prevent it from freezing the UI or crashing the system.

1. **Process launch** — `runner.py` calls `QProcess.start("python3", [temp_file])`. The Qt event loop handles stdout/stderr asynchronously via signals — no manual threads needed.
2. **Output routing** — stdout → `stdout_received` → `TerminalPanel`; stderr → `stderr_received` → `TerminalPanel`.
3. **Timeout** — a `QTimer` kills the process after 30 seconds if it has not exited.
4. **Cleanup** — the temp file is deleted and `execution_finished(exit_code)` is emitted.

```
[Run button]
    │  execution_requested(code)
    ▼
runner.py
  → temp .py file
  → QProcess.start("python3", [temp_file])
      stdout  →  stdout_received  →  TerminalPanel
      stderr  →  stderr_received  →  TerminalPanel
      QTimer 30s  →  process.kill()
      finished    →  execution_finished(exit_code)
```

### REPL mode (⚡ REPL button / F9)

A persistent `python3 -u -i` process runs inside `ReplPanel`. Input is sent via `QProcess.write()`; output is read from stdout/stderr signals. OSC/ANSI escape codes and Python's interactive prompts are filtered from stderr before display.

```
[REPL toggle ON]
    │  repl_mode_changed(True)
    ▼
main_window  →  hide editor + terminal, show ReplPanel
ReplPanel.showEvent()  →  QProcess.start("python3", ["-u", "-i"])

[User types expression]
    │  QProcess.write(text + "\n")
    ▼
stdout/stderr  →  _CTRL_RE strips escape codes
               →  _filter_stderr drops prompts & banner
               →  append to output view
```

---

## 6. Development Roadmap

| Phase | Status | Goal |
|-------|--------|------|
| **1 — IDE Foundation** | ✅ Done | PyQt5 window, editor with line numbers, output terminal, toolbar, activity bar sidebar, event bus, QProcess runner, theme system |
| **2 — REPL Mode** | ✅ Done | Interactive Python console, escape-code filtering, toolbar integration |
| **3 — Curriculum** | 🔲 Planned | Lesson browser (`QTreeWidget`), bundled project templates, SQLite student profiles and progress tracking |
| **4 — Extensions** | 🔲 Future | AI Assistant and Hardware/GPIO as optional `IFeature` plugins |

---

## 7. Running the App

### ARM (Armbian / Raspberry Pi OS)

```bash
# 1. Install system Qt
sudo apt update
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwidgets python3-pyqt5.qtgui python3-pyqt5.qtcore

# 2. Create venv that inherits system PyQt5
python3 -m venv --system-site-packages ~/.venvs/neo-code
source ~/.venvs/neo-code/bin/activate
pip install neo-code
neo-code
```

### x86 / Desktop

```bash
python3 -m venv ~/.venvs/neo-code
source ~/.venvs/neo-code/bin/activate
pip install neo-code
neo-code
```

### From source

```bash
git clone https://github.com/MEO-3/neo-code.git
cd neo-code
python3 -m venv --system-site-packages .venv   # drop --system-site-packages on x86
source .venv/bin/activate
pip install -e .
python -m neo_code
```
