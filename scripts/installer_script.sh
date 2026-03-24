#!/usr/bin/env bash
# ==============================================================================
# NEO Code Installer
# First-time installation script for NEO Code educational Python IDE.
# Handles ARM (Armbian/Raspberry Pi) and x86 platforms automatically.
#
# Usage:
#   Local:  bash scripts/installer_script.sh
#   Remote: curl -sSL https://raw.githubusercontent.com/MEO-3/neo-code/main/scripts/installer_script.sh | bash
#
# Options:
#   --no-desktop   Skip .desktop file and icon installation
#   --no-venv      Install into system Python instead of a virtualenv
#   --uninstall    Remove NEO Code installation
# ==============================================================================
set -euo pipefail

# -- Configuration ------------------------------------------------------------
APP_NAME="neo-code"
INSTALL_DIR="$HOME/.local/share/neo-code"
VENV_DIR="$INSTALL_DIR/venv"
BIN_LINK="$HOME/.local/bin/neo-code"
DESKTOP_FILE="$HOME/.local/share/applications/neo-code.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/128x128/apps"
ICON_FILE="$ICON_DIR/neo-code.png"
PYPI_PACKAGE="neo-code"
NON_QT_DEPS=("jedi>=0.19.0" "pyflakes>=3.2.0")

# -- Parse arguments -----------------------------------------------------------
SKIP_DESKTOP=false
USE_VENV=true
UNINSTALL=false

for arg in "$@"; do
    case "$arg" in
        --no-desktop) SKIP_DESKTOP=true ;;
        --no-venv)    USE_VENV=false ;;
        --uninstall)  UNINSTALL=true ;;
        *)            echo "Unknown option: $arg"; exit 1 ;;
    esac
done

# -- Helpers -------------------------------------------------------------------
info()  { echo -e "\033[1;32m[INFO]\033[0m  $*"; }
warn()  { echo -e "\033[1;33m[WARN]\033[0m  $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; }

require_cmd() {
    if ! command -v "$1" &>/dev/null; then
        error "'$1' is required but not found. Please install it first."
        exit 1
    fi
}

detect_arch() {
    local machine
    machine="$(uname -m)"
    case "$machine" in
        aarch64|armv7l|armv6l) echo "arm" ;;
        x86_64|i686|i386)     echo "x86" ;;
        *)                    echo "unknown" ;;
    esac
}

# -- Uninstall -----------------------------------------------------------------
do_uninstall() {
    info "Uninstalling NEO Code..."

    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
        info "Removed virtualenv: $VENV_DIR"
    fi

    if [ -L "$BIN_LINK" ]; then
        rm -f "$BIN_LINK"
        info "Removed symlink: $BIN_LINK"
    fi

    if [ -f "$DESKTOP_FILE" ]; then
        rm -f "$DESKTOP_FILE"
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
        info "Removed desktop entry: $DESKTOP_FILE"
    fi

    if [ -f "$ICON_FILE" ]; then
        rm -f "$ICON_FILE"
        info "Removed icon: $ICON_FILE"
    fi

    # Clean up install dir if empty
    rmdir "$INSTALL_DIR" 2>/dev/null || true

    info "NEO Code has been uninstalled."
    exit 0
}

if [ "$UNINSTALL" = true ]; then
    do_uninstall
fi

# -- Pre-flight checks ---------------------------------------------------------
ARCH="$(detect_arch)"
info "Detected architecture: $ARCH ($(uname -m))"

require_cmd python3

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PYTHON_MAJOR="${PYTHON_VERSION%%.*}"
PYTHON_MINOR="${PYTHON_VERSION##*.}"

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    error "Python 3.11+ is required (found $PYTHON_VERSION)."
    exit 1
fi
info "Python $PYTHON_VERSION found."

# -- Step 1: Install system dependencies (ARM) --------------------------------
install_system_deps() {
    if [ "$ARCH" = "arm" ]; then
        info "ARM detected — installing PyQt5 via apt (avoids building from source)..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq \
            python3-pyqt5 \
            # python3-pyqt5.qtwidgets \
            # python3-pyqt5.qtgui \
            # python3-pyqt5.qtcore \
            python3-venv \
            python3-pip
    elif [ "$ARCH" = "x86" ]; then
        info "x86 detected — PyQt5 will be installed via pip."
        # Ensure venv and pip are available
        if ! python3 -m venv --help &>/dev/null; then
            info "Installing python3-venv..."
            sudo apt-get update -qq
            sudo apt-get install -y -qq python3-venv
        fi
    else
        warn "Unknown architecture '$(uname -m)'. Proceeding with pip-based install."
    fi
}

install_system_deps

# -- Step 2: Create virtualenv ------------------------------------------------
install_in_venv() {
    mkdir -p "$INSTALL_DIR"

    if [ "$ARCH" = "arm" ]; then
        # Use --system-site-packages so the venv can access apt-installed PyQt5
        info "Creating virtualenv with system-site-packages (for apt PyQt5)..."
        python3 -m venv --system-site-packages "$VENV_DIR"
    else
        info "Creating isolated virtualenv..."
        python3 -m venv "$VENV_DIR"
    fi

    # Upgrade pip inside venv
    "$VENV_DIR/bin/pip" install --upgrade pip --quiet

    if [ "$ARCH" = "arm" ]; then
        # Install non-Qt dependencies first
        info "Installing Python dependencies (excluding PyQt5)..."
        "$VENV_DIR/bin/pip" install --quiet "${NON_QT_DEPS[@]}"
        # Install neo-code without pulling in PyQt5 from pip
        info "Installing NEO Code (--no-deps to skip PyQt5 rebuild)..."
        "$VENV_DIR/bin/pip" install --quiet --no-deps "$PYPI_PACKAGE"
    else
        # On x86, pip wheel for PyQt5 is available — install everything normally
        info "Installing NEO Code and all dependencies..."
        "$VENV_DIR/bin/pip" install --quiet "$PYPI_PACKAGE"
    fi

    # Create bin symlink
    mkdir -p "$(dirname "$BIN_LINK")"
    ln -sf "$VENV_DIR/bin/neo-code" "$BIN_LINK"
    info "Linked $BIN_LINK -> $VENV_DIR/bin/neo-code"
}

install_without_venv() {
    local pip_args=()
    # On modern Debian/Ubuntu, --break-system-packages may be needed
    if python3 -m pip install --help 2>&1 | grep -q "break-system-packages"; then
        pip_args+=(--break-system-packages)
    fi

    if [ "$ARCH" = "arm" ]; then
        info "Installing Python dependencies (excluding PyQt5)..."
        python3 -m pip install "${pip_args[@]}" --quiet "${NON_QT_DEPS[@]}"
        info "Installing NEO Code (--no-deps to skip PyQt5 rebuild)..."
        python3 -m pip install "${pip_args[@]}" --quiet --no-deps "$PYPI_PACKAGE"
    else
        info "Installing NEO Code and all dependencies..."
        python3 -m pip install "${pip_args[@]}" --quiet "$PYPI_PACKAGE"
    fi
}

if [ "$USE_VENV" = true ]; then
    install_in_venv
else
    install_without_venv
fi

# -- Step 3: Verify installation -----------------------------------------------
if [ "$USE_VENV" = true ]; then
    NEO_BIN="$VENV_DIR/bin/neo-code"
else
    NEO_BIN="$(command -v neo-code 2>/dev/null || true)"
fi

if [ -z "$NEO_BIN" ] || [ ! -x "$NEO_BIN" ]; then
    error "Installation verification failed — 'neo-code' binary not found."
    exit 1
fi
info "Verified: $NEO_BIN"

# -- Step 4: Desktop integration -----------------------------------------------
install_desktop_entry() {
    if [ "$SKIP_DESKTOP" = true ]; then
        info "Skipping desktop integration (--no-desktop)."
        return
    fi

    local exec_path="$NEO_BIN"

    # Install icon if available in the package
    local icon_name="neo-code"
    local pkg_icon
    pkg_icon="$(python3 -c "
import importlib.resources, pathlib, sys
try:
    ref = importlib.resources.files('neo_code') / 'resources' / 'neo-code.png'
    with importlib.resources.as_file(ref) as p:
        print(p)
except Exception:
    pass
" 2>/dev/null || true)"

    if [ -n "$pkg_icon" ] && [ -f "$pkg_icon" ]; then
        mkdir -p "$ICON_DIR"
        cp "$pkg_icon" "$ICON_FILE"
        icon_name="$ICON_FILE"
        info "Installed icon: $ICON_FILE"
    fi

    # Write .desktop file
    mkdir -p "$(dirname "$DESKTOP_FILE")"
    cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NEO Code
GenericName=Educational Python IDE
Comment=Python IDE for STEM and Robotics students
Exec=$exec_path
Icon=$icon_name
Terminal=false
Categories=Education;Development;IDE;
Keywords=python;ide;code;kids;stem;robotics;
StartupNotify=true
EOF

    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    info "Created desktop entry: $DESKTOP_FILE"
}

install_desktop_entry

# -- Step 5: Ensure ~/.local/bin is in PATH ------------------------------------
ensure_path() {
    local bin_dir="$HOME/.local/bin"
    if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
        warn "$bin_dir is not in your PATH."

        local shell_rc=""
        case "$(basename "$SHELL")" in
            zsh)  shell_rc="$HOME/.zshrc" ;;
            bash) shell_rc="$HOME/.bashrc" ;;
            *)    shell_rc="$HOME/.profile" ;;
        esac

        if [ -f "$shell_rc" ] && ! grep -q 'local/bin' "$shell_rc"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_rc"
            info "Added $bin_dir to PATH in $shell_rc"
            info "Run 'source $shell_rc' or open a new terminal to use 'neo-code'."
        fi
    fi
}

ensure_path

# -- Done ----------------------------------------------------------------------
echo ""
info "=========================================="
info "  NEO Code installed successfully!"
info "=========================================="
echo ""
echo "  Run:  neo-code"
echo ""
if [ "$USE_VENV" = true ]; then
    echo "  Installed in: $VENV_DIR"
fi
echo "  Uninstall:    bash $0 --uninstall"
echo ""
