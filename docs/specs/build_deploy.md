# NEO CODE — Build & Deploy Guide

## Contents

1. [Development Setup](#1-development-setup)
2. [Running Locally](#2-running-locally)
3. [Building a Release Wheel](#3-building-a-release-wheel)
4. [Publishing to PyPI](#4-publishing-to-pypi)
5. [Installing from PyPI](#5-installing-from-pypi)
6. [Deploying to an Armbian Device](#6-deploying-to-an-armbian-device)
7. [Desktop Integration](#7-desktop-integration)
8. [Autostart on Boot](#8-autostart-on-boot)
9. [Updating an Existing Install](#9-updating-an-existing-install)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Development Setup

### Requirements

- Python **3.11** or later
- `conda` or `venv` for isolation (strongly recommended — system Python on Armbian is externally managed)
- `git`

### With conda (recommended on dev machine)

```bash
conda create -n neo python=3.11
conda activate neo
pip install -e ".[dev]"   # installs PyQt6, Jedi, pyflakes + hatch for building
```

### With venv (recommended on Armbian target)

```bash
python3.11 -m venv ~/.venvs/neo-code
source ~/.venvs/neo-code/bin/activate
pip install -e .
```

### Install build tools

```bash
pip install hatch
```

---

## 2. Running Locally

```bash
# From the repo root, with the env active:
python -m neo_code

# Or, if installed via pip install -e .:
neo-code
```

Keyboard shortcuts:

| Action | Shortcut |
|--------|---------|
| Run code | F5 |
| Stop execution | F6 |
| New file | Ctrl+N |
| Open file | Ctrl+O |
| Save file | Ctrl+S |

---

## 3. Building a Release Wheel

The project uses **hatchling** as the build backend. The output is a **pure-Python wheel** — architecture-independent, so a wheel built on your x86 dev machine installs on ARM without modification.

```bash
# From the repo root, with the env active:
hatch build
```

Output:

```
dist/
├── neo_code-0.1.0-py3-none-any.whl   ← install this on the target device
└── neo_code-0.1.0.tar.gz             ← source distribution
```

### Bumping the version

Edit `version` in `pyproject.toml` before building:

```toml
[project]
version = "0.2.0"
```

---

## 4. Publishing to PyPI

### 4.1 One-time setup

**Create a PyPI account** at [https://pypi.org/account/register/](https://pypi.org/account/register/).

Install publish tools (already in `[project.optional-dependencies]` dev):

```bash
pip install hatch twine
```

**Create an API token** at [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/) and store it:

```bash
# Option A — store in ~/.pypirc (recommended for local publishing)
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
EOF
chmod 600 ~/.pypirc
```

### 4.2 Bump the version

Edit `pyproject.toml` before every release:

```toml
[project]
version = "0.2.0"
```

Also update the `Development Status` classifier when leaving alpha:

```toml
# Alpha   → "Development Status :: 3 - Alpha"
# Beta    → "Development Status :: 4 - Beta"
# Stable  → "Development Status :: 5 - Production/Stable"
```

### 4.3 Build

```bash
# Clean previous dist/ artifacts first
rm -rf dist/
hatch build
```

Output:

```
dist/
├── neo_code-0.2.0-py3-none-any.whl   ← pure-Python, works on x86 and ARM
└── neo_code-0.2.0.tar.gz
```

### 4.4 Check the package before uploading

```bash
twine check dist/*
```

All items should report `PASSED`. Fix any warnings before uploading.

### 4.5 Upload to PyPI

```bash
twine upload dist/*
```

Your package is now live at `https://pypi.org/project/neo-code/`.

### 4.6 Test on TestPyPI first (optional but recommended)

TestPyPI is a sandbox that mirrors real PyPI without affecting production:

```bash
twine upload --repository testpypi dist/*

# Install from TestPyPI to verify
pip install --index-url https://test.pypi.org/simple/ neo-code
```

### 4.7 Automate with GitHub Actions

Create `.github/workflows/publish.yml` to publish automatically on every git tag:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v*"          # triggers on v0.1.0, v0.2.0, etc.

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi                  # set PYPI_TOKEN in GitHub repo secrets
    permissions:
      id-token: write                  # required for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install hatch
      - run: hatch build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

Then to release:

```bash
git tag v0.2.0
git push origin v0.2.0
```

---

## 5. Installing from PyPI

Once published, anyone installs with:

```bash
pip install neo-code
neo-code
```

On Armbian or any system-managed Python, use a venv:

```bash
python3 -m venv ~/.venvs/neo-code
source ~/.venvs/neo-code/bin/activate
pip install neo-code
neo-code
```

To upgrade to a newer release:

```bash
pip install --upgrade neo-code
```

---

## 6. Deploying to an Armbian Device

### 6.1 Prerequisites on the device

Armbian ships Python 3.11+ on recent images. Confirm:

```bash
python3 --version   # must be 3.11+
```

PyQt6 provides pre-built wheels for **`linux/aarch64`** on PyPI — no compilation needed.

> **Note:** If `pip install PyQt6` fails with a missing wheel error, ensure pip is up to date:
> `pip install --upgrade pip`

### 6.2 Copy the wheel to the device

```bash
# From your dev machine — replace IP and username as needed
scp dist/neo_code-0.1.0-py3-none-any.whl user@192.168.1.100:/tmp/
```

### 6.3 Install on the device

SSH into the device:

```bash
ssh user@192.168.1.100
```

Create a dedicated venv and install:

```bash
python3 -m venv ~/.venvs/neo-code
source ~/.venvs/neo-code/bin/activate
pip install --upgrade pip
pip install /tmp/neo_code-0.1.0-py3-none-any.whl
```

Verify:

```bash
neo-code --help 2>/dev/null || python -m neo_code &
```

### 6.4 Check display is available

NEO CODE requires a running display server (X11 or Wayland). On a headless Armbian server image you must install a desktop environment first. On desktop Armbian images (XFCE, KDE, etc.) this works out of the box.

```bash
# Confirm DISPLAY is set
echo $DISPLAY   # should print something like :0
```

---

## 7. Desktop Integration

Create a `.desktop` file so NEO CODE appears in the application menu.

### 7.1 Create the launcher

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/neo-code.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=NEO Code
GenericName=Educational Python IDE
Comment=Python IDE for STEM and Robotics students
Exec=/home/USER/.venvs/neo-code/bin/neo-code
Icon=neo-code
Terminal=false
Categories=Education;Development;IDE;
Keywords=python;ide;code;kids;stem;
StartupNotify=true
EOF
```

Replace `USER` with the actual username, or use the absolute path output of:

```bash
which neo-code   # e.g. /home/vinh/.venvs/neo-code/bin/neo-code
```

### 7.2 Optional: add an icon

Copy an icon to the icons directory:

```bash
mkdir -p ~/.local/share/icons/hicolor/128x128/apps/
cp /path/to/neo-code-icon.png ~/.local/share/icons/hicolor/128x128/apps/neo-code.png
gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true
```

### 7.3 Refresh the application database

```bash
update-desktop-database ~/.local/share/applications/
```

---

## 8. Autostart on Boot

For a kiosk-style setup where NEO CODE launches automatically when the student logs in:

### Via XDG autostart (per-user)

```bash
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/neo-code.desktop ~/.config/autostart/
```

### Via systemd user service (more control)

```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/neo-code.service << 'EOF'
[Unit]
Description=NEO Code Educational IDE
After=graphical-session.target

[Service]
Type=simple
ExecStart=/home/USER/.venvs/neo-code/bin/neo-code
Restart=on-failure
Environment=DISPLAY=:0

[Install]
WantedBy=graphical-session.target
EOF

systemctl --user enable neo-code
systemctl --user start neo-code
```

---

## 9. Updating an Existing Install

### Build a new wheel on your dev machine

```bash
# Bump version in pyproject.toml, then:
hatch build
scp dist/neo_code-0.2.0-py3-none-any.whl user@192.168.1.100:/tmp/
```

### Install the update on the device

```bash
source ~/.venvs/neo-code/bin/activate
pip install --upgrade /tmp/neo_code-0.2.0-py3-none-any.whl
```

No reboot required. If NEO Code is running, restart it:

```bash
pkill -f neo-code && neo-code &
# or, if using systemd:
systemctl --user restart neo-code
```

---

## 10. Troubleshooting

### `ModuleNotFoundError: No module named 'PyQt6'`

The app is being run outside the venv. Activate it first:

```bash
source ~/.venvs/neo-code/bin/activate
neo-code
```

Or run via the full path:

```bash
~/.venvs/neo-code/bin/neo-code
```

### `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"`

Missing X11 libraries. Install them:

```bash
sudo apt install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
                 libxcb-randr0 libxcb-render-util0 libxcb-xkb1 libxkbcommon-x11-0
```

### `pip install PyQt6` fails on ARM

Upgrade pip first — older pip versions do not resolve the aarch64 wheel:

```bash
pip install --upgrade pip
pip install PyQt6
```

If still failing, install from the Qt Company's own index:

```bash
pip install --index-url https://download.qt.io/snapshots/ci/pyside/dev/latest/pip/ PyQt6
```

### Black / blank window on Wayland

Force X11 backend:

```bash
QT_QPA_PLATFORM=xcb neo-code
```

Add to the `.desktop` `Exec` line for a permanent fix:

```ini
Exec=env QT_QPA_PLATFORM=xcb /home/USER/.venvs/neo-code/bin/neo-code
```

### High CPU on older ARM boards

Reduce animation load by forcing the software renderer:

```bash
LIBGL_ALWAYS_SOFTWARE=1 neo-code
```
