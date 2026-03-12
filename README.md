# NEO Code

**An educational Python IDE for STEM & Robotics students (ages 6–12)**

NEO Code is a lightweight, kid-friendly Python IDE designed to run on low-resource devices such as Armbian single-board computers (2 GB RAM). It provides a clean coding environment with structured lessons, visual turtle graphics output, and student progress tracking — no internet required.

---

## Features

- 🟢 **Python editor** — syntax highlighting, line numbers, debounced code-change events
- ▶️ **Run & Stop** — sandboxed `QProcess` execution with 30-second timeout (F5 / F6)
- 📤 **Output panel** — collapsible console showing stdout and stderr in colour
- 📖 **Lesson sidebar** — VS Code-style activity bar with curriculum browser *(Phase 3)*
- 🐢 **Turtle canvas** — visual turtle graphics output without opening a separate window *(Phase 2)*
- 🎨 **Green theme** — clean white + #32A852 green palette, easy on young eyes

## Requirements

- Python **3.11+**
- Linux (tested on x86 and ARM/Armbian)
- A running display server (X11 or Wayland)

## Installation

```bash
pip install neo-code
neo-code
```

> **Tip for Armbian / system-managed Python:** use a venv first.
> ```bash
> python3 -m venv ~/.venvs/neo-code
> source ~/.venvs/neo-code/bin/activate
> pip install neo-code
> neo-code
> ```

## Running from source

```bash
git clone https://github.com/MEO-3/neo-code.git
cd neo-code
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -m neo_code
```

## Keyboard shortcuts

| Action | Shortcut |
|--------|---------|
| Run code | F5 |
| Stop execution | F6 |
| New file | Ctrl+N |
| Open file | Ctrl+O |
| Save file | Ctrl+S |

## Project status

| Phase | Status | Description |
|-------|--------|-------------|
| 1 — IDE Foundation | ✅ Done | Editor, terminal, toolbar, sidebar, theme, event bus, QProcess runner |
| 2 — Turtle canvas | 🔲 Planned | Visual turtle output via proxy injection |
| 3 — Curriculum | 🔲 Planned | Lesson browser, project templates, student progress |

## License

MIT
