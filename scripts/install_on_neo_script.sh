#!/bin/bash
set -e

echo "=== NEO Code Installer ==="
echo "Installing dependencies for neo-code..."

# Update package list
sudo apt-get update

# Install PyQt5 via apt (avoids building from source on ARM)
echo "[1/3] Installing PyQt5 via apt..."
sudo apt-get install -y python3-pyqt5

# Install pip if not present
sudo apt-get install -y python3-pip

# Install remaining Python dependencies via pip
echo "[2/3] Installing Jedi and pyflakes via pip..."
pip3 install --break-system-packages "jedi>=0.19.0" "pyflakes>=3.2.0"

# Install neo-code itself
echo "[3/3] Installing neo-code..."
pip3 install --break-system-packages --no-deps .

# Add pip user bin to PATH if not already present
PIP_BIN="$HOME/.local/bin"
if [[ ":$PATH:" != *":$PIP_BIN:"* ]]; then
    echo "Adding $PIP_BIN to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    export PATH="$PIP_BIN:$PATH"
fi

echo ""
echo "Installation complete. Run 'neo-code' to start."
