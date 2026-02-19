#!/bin/bash
# ============================================================
# NEO CODE - Build deployment package for ARM64
# Creates: neo-code-<version>-arm64.tar.gz
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION=$(grep 'version' "$PROJECT_DIR/pyproject.toml" | head -1 | sed 's/.*"\(.*\)".*/\1/')
PACKAGE_NAME="neo-code-${VERSION}-arm64"
BUILD_DIR="/tmp/${PACKAGE_NAME}"
OUTPUT_DIR="${PROJECT_DIR}/dist"

echo "============================================================"
echo " NEO CODE Package Builder"
echo " Version: $VERSION"
echo " Output:  $OUTPUT_DIR/${PACKAGE_NAME}.tar.gz"
echo "============================================================"
echo ""

# Clean
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

# Copy source (exclude dev files)
echo "[1/4] Copying source..."
rsync -a \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.mypy_cache' \
    --exclude='.pytest_cache' \
    --exclude='.ruff_cache' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='*.egg-info' \
    --exclude='.claude' \
    --exclude='*.jsonl' \
    "$PROJECT_DIR/" "$BUILD_DIR/"

# Ensure deployment scripts are executable
echo "[2/4] Setting permissions..."
chmod +x "$BUILD_DIR/deployment/install-arm64.sh"

# Create quick-start README
echo "[3/4] Creating README..."
cat > "$BUILD_DIR/README-INSTALL.txt" << 'EOF'
============================================================
  NEO CODE - Educational Python IDE
  Quick Install Guide for ARM64 (Armbian/Debian)
============================================================

REQUIREMENTS:
  - ARM64 (aarch64) system
  - RAM: 2 GB+
  - Disk: 2 GB+ free
  - OS: Armbian / Debian 12 / Ubuntu 22.04+

INSTALL (1 lenh):

  chmod +x deployment/install-arm64.sh
  ./deployment/install-arm64.sh

Script se tu dong:
  1. Cau hinh ZRAM swap (bao ve flash)
  2. Cai system packages (Qt6, Python, fonts)
  3. Copy source code to /opt/neo-code
  4. Tao virtualenv + cai dependencies
  5. Tao config toi uu cho ARM
  6. Tao launcher + desktop entry
  7. Kiem tra cai dat

SAU KHI CAI:

  neo-code              # Chay tu terminal
  /opt/neo-code/run.sh  # Chay truc tiep

DOC THEM:
  deployment/INSTALL_ARM64.md   - Huong dan chi tiet tung buoc
  deployment/OPTIMIZE_FLASH.md  - Toi uu dung luong flash

============================================================
EOF

# Build tarball
echo "[4/4] Building tarball..."
cd /tmp
tar czf "$OUTPUT_DIR/${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

# Show result
SIZE=$(du -sh "$OUTPUT_DIR/${PACKAGE_NAME}.tar.gz" | cut -f1)
echo ""
echo "============================================================"
echo " Package created:"
echo "   $OUTPUT_DIR/${PACKAGE_NAME}.tar.gz"
echo "   Size: $SIZE"
echo ""
echo " Deploy to ARM64 device:"
echo "   scp $OUTPUT_DIR/${PACKAGE_NAME}.tar.gz user@device:~/"
echo "   ssh user@device"
echo "   tar xzf ${PACKAGE_NAME}.tar.gz"
echo "   cd ${PACKAGE_NAME}"
echo "   ./deployment/install-arm64.sh"
echo "============================================================"

# Cleanup
rm -rf "$BUILD_DIR"
