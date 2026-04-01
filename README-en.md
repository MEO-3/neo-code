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

### Quick install (recommended)

The installer script automatically detects your platform (ARM or x86) and handles everything — including PyQt5, virtualenv setup, and desktop integration:

```bash
curl -sSL https://raw.githubusercontent.com/MEO-3/neo-code/main/scripts/installer_script.sh | bash
```

Or install on Neo One:

```bash
curl -sSL https://raw.githubusercontent.com/MEO-3/neo-code/main/scripts/install_on_neo.sh | bash
```

Or clone the repo first and run locally:

```bash
git clone https://github.com/MEO-3/neo-code.git
cd neo-code
bash scripts/installer_script.sh
```

This will:
- Install PyQt5 via **apt** on ARM (no compiling from source)
- Install PyQt5 via **pip** on x86 (pre-built wheel)
- Create a virtualenv at `~/.local/share/neo-code/venv`
- Add a `neo-code` command to `~/.local/bin`
- Create a `.desktop` launcher entry

**Installer options:**

| Flag | Effect |
|------|--------|
| `--no-desktop` | Skip `.desktop` file and icon installation |
| `--no-venv` | Install into system Python instead of a virtualenv |
| `--uninstall` | Remove NEO Code and all associated files |

---

### Manual install

If you prefer to install manually:

#### ARM (Armbian / Raspberry Pi OS)

```bash
# 1. Install PyQt5 from apt (avoids building from source)
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwidgets \
    python3-pyqt5.qtgui python3-pyqt5.qtcore python3-venv

# 2. Create venv with system-site-packages (to access apt PyQt5)
python3 -m venv --system-site-packages ~/.local/share/neo-code/venv
source ~/.local/share/neo-code/venv/bin/activate

# 3. Install neo-code without pulling PyQt5 from pip
pip install jedi pyflakes
pip install --no-deps neo-code

neo-code
```

#### x86 / Desktop Linux

```bash
python3 -m venv ~/.local/share/neo-code/venv
source ~/.local/share/neo-code/venv/bin/activate
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
