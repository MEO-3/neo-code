#!/usr/bin/env bash
# ==============================================================================
# NEO Code Installer
# First-time installation script for NEO Code educational Python IDE.
# Handles ARM (Armbian/Raspberry Pi) and x86 platforms automatically.
#
# Usage:
#   Local:  bash scripts/install_on_neo.sh
#   Remote: curl -sSL https://raw.githubusercontent.com/MEO-3/neo-code/main/scripts/install_on_neo.sh | bash
#
# Options:
#   --no-desktop   Skip .desktop file and icon installation
#   --uninstall    Remove NEO Code installation
# ==============================================================================
set -euo pipefail

# -- Configuration ------------------------------------------------------------
APP_NAME="neo-code"
DISPLAY_NAME="NEO Code"
BIN_LINK="$HOME/.local/bin/neo-code"
DESKTOP_FILE="$HOME/.local/share/applications/neo-code.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/128x128/apps"
ICON_FILE="$ICON_DIR/neo-code.png"
PYPI_PACKAGE="neo-code"
GITHUB_REPO="https://github.com/MEO-3/neo-code.git"

# -- Parse arguments -----------------------------------------------------------
SKIP_DESKTOP=false
UNINSTALL=false

for arg in "$@"; do
    case "$arg" in
        --no-desktop) SKIP_DESKTOP=true ;;
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

# pip install wrapper that adds --break-system-packages when needed
pip_install() {
    local bsp=""
    if python3 -m pip install --help 2>&1 | grep -q "break-system-packages"; then
        bsp="--break-system-packages"
    fi
    python3 -m pip install $bsp "$@"
}

# -- Uninstall -----------------------------------------------------------------
do_uninstall() {
    info "Uninstalling $DISPLAY_NAME..."

    # Remove pip-installed package
    local bsp=""
    if python3 -m pip install --help 2>&1 | grep -q "break-system-packages"; then
        bsp="--break-system-packages"
    fi
    python3 -m pip uninstall -y $bsp "$PYPI_PACKAGE" 2>/dev/null || true

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

    info "$DISPLAY_NAME has been uninstalled."
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

# -- Step 1: Install system dependencies --------------------------------------
install_system_deps() {
    if [ "$ARCH" = "arm" ]; then
        info "ARM detected — installing system dependencies..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq \
            python3-pyqt5 \
            python3-pip \
            git \
            2>/dev/null || true
    elif [ "$ARCH" = "x86" ]; then
        info "x86 detected — PyQt5 will be installed via pip."
    else
        warn "Unknown architecture '$(uname -m)'. Proceeding with pip-based install."
    fi
}

install_system_deps

# -- Step 2: Install package --------------------------------------------------
info "Installing $DISPLAY_NAME..."

if [ "$ARCH" = "arm" ]; then
    # ARM: avoid rebuilding PyQt5 from source — use system apt package
    info "ARM detected — installing without PyQt5 dependency (using system PyQt5)..."
    if ! pip_install --no-deps --quiet "$PYPI_PACKAGE" 2>&1; then
        info "PyPI install failed. Installing from GitHub source..."
        require_cmd git
        pip_install --no-deps "git+${GITHUB_REPO}"
    fi
    # Install non-Qt dependencies separately
    info "Installing Python dependencies (excluding PyQt5)..."
    pip_install --quiet "jedi>=0.19.0" "pyflakes>=3.2.0" "thingbot-telemetrix"
    # Ensure PyQt5 is available (system packages or pip fallback)
    if ! python3 -c "import PyQt5" 2>/dev/null; then
        info "Installing PyQt5 via pip (this may take a while on ARM)..."
        pip_install "PyQt5>=5.15"
    fi
else
    # x86: PyQt5 wheels available, normal install
    if pip_install --quiet "$PYPI_PACKAGE" 2>&1; then
        info "Installed from PyPI."
    else
        info "PyPI install failed. Installing from GitHub source..."
        require_cmd git
        pip_install "git+${GITHUB_REPO}"
    fi
fi

# -- Step 3: Verify installation -----------------------------------------------
# pip installs scripts to ~/.local/bin on Linux
NEO_BIN="$(python3 -c "
import sysconfig, os
scripts = sysconfig.get_path('scripts', 'posix_user')
print(os.path.join(scripts, 'neo-code'))
" 2>/dev/null || echo "$HOME/.local/bin/neo-code")"

if [ ! -f "$NEO_BIN" ]; then
    # Also check if it ended up on the system path
    NEO_BIN="$(command -v neo-code 2>/dev/null || true)"
fi

if [ -z "$NEO_BIN" ] || [ ! -f "$NEO_BIN" ]; then
    error "Installation failed — 'neo-code' binary not found."
    error "Check the output above for errors."
    exit 1
fi

# Ensure symlink in ~/.local/bin
mkdir -p "$(dirname "$BIN_LINK")"
if [ "$NEO_BIN" != "$BIN_LINK" ]; then
    ln -sf "$NEO_BIN" "$BIN_LINK"
fi
info "Verified: $NEO_BIN"

# -- Step 4: Desktop integration -----------------------------------------------
install_desktop_entry() {
    if [ "$SKIP_DESKTOP" = true ]; then
        info "Skipping desktop integration (--no-desktop)."
        return
    fi

    local exec_path="$BIN_LINK"
    local icon_name="neo-code"

    # Try to find icon from installed package
    local pkg_icon
    pkg_icon="$(python3 -c "
import importlib.resources, sys
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
info "  $DISPLAY_NAME installed successfully!"
info "=========================================="
echo ""
echo "  Run:  neo-code"
echo ""
echo "  Uninstall:  curl -sSL https://raw.githubusercontent.com/MEO-3/neo-code/main/scripts/install_on_neo.sh | bash -s -- --uninstall"
echo ""
