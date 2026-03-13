# NEO Code

**An educational Python IDE for STEM & Robotics students (ages 6–12)**

NEO Code is a lightweight, kid-friendly Python IDE designed to run on low-resource devices such as Armbian single-board computers (2 GB RAM). It provides a clean coding environment with structured lessons and an interactive REPL — no internet required.

---

## Features

- 🟢 **Python editor** — syntax highlighting, line numbers, debounced code-change events
- ▶️ **Run & Stop** — sandboxed `QProcess` execution with 30-second timeout (F5 / F6)
- ⚡ **REPL mode** — live interactive Python console backed by a persistent `python3 -i` process (F9)
- 📤 **Output panel** — collapsible console showing stdout and stderr in colour
- 📖 **Lesson sidebar** — VS Code-style activity bar with curriculum browser
- 🎨 **Green theme** — clean white + #32A852 green palette, easy on young eyes

---

## Requirements

- Python **3.11+**
- Linux (tested on x86 and ARM/Armbian)
- A running display server (X11 or Wayland)
- Qt 5.15 libraries (installed via apt **or** bundled inside the pip wheel)

---

## Installation

### 1 — Install system Qt libraries (Debian / Ubuntu / Armbian)

PyQt5 pip wheels bundle their own Qt on x86, but on **ARM** boards (Armbian, Raspberry Pi OS, etc.) it is faster and more reliable to use the distro packages:

```bash
sudo apt update
sudo apt install -y \
    python3-pyqt5 \
    python3-pyqt5.qtwidgets \
    python3-pyqt5.qtgui \
    python3-pyqt5.qtcore \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a
```

> **x86 / desktop users** can skip this step — the pip wheel includes Qt automatically.

---

### 2 — Install NEO Code

#### Option A — System Python (simplest, ARM-recommended)

```bash
pip install neo-code
neo-code
```

#### Option B — Virtual environment with system Qt (ARM-recommended)

Use `--system-site-packages` so the venv can see the apt-installed PyQt5:

```bash
python3 -m venv --system-site-packages ~/.venvs/neo-code
source ~/.venvs/neo-code/bin/activate
pip install neo-code
neo-code
```

#### Option C — Fully isolated venv (x86 / desktop)

```bash
python3 -m venv ~/.venvs/neo-code
source ~/.venvs/neo-code/bin/activate
pip install neo-code
neo-code
```

---

## Running from source

```bash
git clone https://github.com/MEO-3/neo-code.git
cd neo-code

# ARM — reuse system PyQt5
python3 -m venv --system-site-packages .venv

# x86 — fully isolated
# python3 -m venv .venv

source .venv/bin/activate
pip install -e .
python -m neo_code
```

---

## Keyboard shortcuts

| Action | Shortcut |
|--------|---------|
| Run code | F5 |
| Stop execution | F6 |
| Toggle REPL mode | F9 |
| New file | Ctrl+N |
| Open file | Ctrl+O |
| Save file | Ctrl+S |

---

## Project status

| Phase | Status | Description |
|-------|--------|-------------|
| 1 — IDE Foundation | ✅ Done | Editor, terminal, toolbar, sidebar, theme, event bus, QProcess runner |
| 2 — REPL mode | ✅ Done | Interactive Python console with persistent process, escape-code filtering |
| 3 — Curriculum | 🔲 Planned | Lesson browser, project templates, student progress |

---

## License

MIT
