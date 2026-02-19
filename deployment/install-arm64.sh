#!/bin/bash
# ============================================================
# NEO CODE - Auto Install Script for ARM64 (Armbian/Debian)
# Target: ARM Cortex-A53 | RAM 2GB | eMMC 16GB
# OS: Armbian / Debian 12 / Ubuntu 22.04+ aarch64
# ============================================================
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

INSTALL_DIR="/opt/neo-code"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="$(dirname "$SCRIPT_DIR")"

log()  { echo -e "${GREEN}[NEO CODE]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ============================================================
echo -e "${CYAN}"
echo "  _   _ _____ ___    ____ ___  ____  _____ "
echo " | \ | | ____/ _ \  / ___/ _ \|  _ \| ____|"
echo " |  \| |  _|| | | || |  | | | | | | |  _|  "
echo " | |\  | |__| |_| || |__| |_| | |_| | |___ "
echo " |_| \_|_____\___/  \____\___/|____/|_____|"
echo ""
echo " Educational Python IDE for STEM/Robotics"
echo " ARM64 Installer v1.0"
echo -e "${NC}"
echo "============================================================"
echo ""

# ============================================================
# Pre-flight checks
# ============================================================
log "Kiem tra he thong..."

# Check root
if [[ $EUID -eq 0 ]]; then
    err "Khong chay bang root. Dung: ./install-arm64.sh"
fi

# Check arch
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" ]]; then
    warn "Architecture: $ARCH (khong phai aarch64)"
    read -p "Van tiep tuc? (y/N): " confirm
    [[ "$confirm" =~ ^[yY]$ ]] || exit 0
fi

# Check RAM
TOTAL_RAM_MB=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)
log "RAM: ${TOTAL_RAM_MB} MB"
if [[ $TOTAL_RAM_MB -lt 1500 ]]; then
    warn "RAM thap ($TOTAL_RAM_MB MB). Can toi thieu 1.5 GB."
fi

# Check disk
ROOT_FREE_MB=$(df / --output=avail -BM | tail -1 | tr -d ' M')
log "Disk trong: ${ROOT_FREE_MB} MB"
if [[ $ROOT_FREE_MB -lt 2000 ]]; then
    err "Khong du disk. Can toi thieu 2 GB trong."
fi

# Check Python
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3; do
    if command -v $cmd &>/dev/null; then
        PY_VER=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PY_MAJOR=$(echo $PY_VER | cut -d. -f1)
        PY_MINOR=$(echo $PY_VER | cut -d. -f2)
        if [[ $PY_MAJOR -ge 3 && $PY_MINOR -ge 11 ]]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

echo ""
echo "============================================================"
echo " He thong:     $(uname -r) ($ARCH)"
echo " RAM:          ${TOTAL_RAM_MB} MB"
echo " Disk trong:   ${ROOT_FREE_MB} MB"
echo " Python:       ${PYTHON_CMD:-CHUA CO (se cai)}"
echo " Source:       $SOURCE_DIR"
echo " Install to:   $INSTALL_DIR"
echo "============================================================"
echo ""
read -p "Bat dau cai dat? (Y/n): " confirm
[[ "$confirm" =~ ^[nN]$ ]] && exit 0

# ============================================================
# Step 1: ZRAM Swap
# ============================================================
log "[1/7] Cau hinh ZRAM swap..."

if ! swapon --show 2>/dev/null | grep -q zram; then
    sudo apt install -y zram-tools 2>/dev/null || true

    if command -v zramctl &>/dev/null; then
        sudo tee /etc/default/zramswap > /dev/null << 'ZRAM_EOF'
ALGO=zstd
PERCENT=50
PRIORITY=100
ZRAM_EOF
        sudo systemctl enable zramswap 2>/dev/null || true
        sudo systemctl restart zramswap 2>/dev/null || true
        sudo sysctl -w vm.swappiness=60 > /dev/null 2>&1
        grep -q 'vm.swappiness=60' /etc/sysctl.conf 2>/dev/null || \
            echo 'vm.swappiness=60' | sudo tee -a /etc/sysctl.conf > /dev/null
        log "  ZRAM swap da bat"
    else
        warn "  Khong cai duoc zram-tools, bo qua"
    fi
else
    log "  ZRAM swap da co san"
fi

# ============================================================
# Step 2: System packages
# ============================================================
log "[2/7] Cai system packages..."

sudo apt update -qq

# Build tools
sudo apt install -y --no-install-recommends \
    build-essential pkg-config cmake \
    2>/dev/null || warn "  Mot so build tools khong cai duoc"

# Python
if [[ -z "$PYTHON_CMD" ]]; then
    log "  Cai Python 3.11+..."
    if sudo apt install -y python3.11 python3.11-dev python3.11-venv 2>/dev/null; then
        PYTHON_CMD=python3.11
    elif sudo apt install -y python3 python3-dev python3-venv 2>/dev/null; then
        PYTHON_CMD=python3
    else
        err "Khong cai duoc Python 3.11+. Cai thu cong truoc."
    fi
else
    sudo apt install -y --no-install-recommends \
        python3-dev python3-venv python3-pip \
        2>/dev/null || true
fi

log "  Python: $($PYTHON_CMD --version)"

# Qt6 + Display
log "  Cai Qt6 libraries..."
sudo apt install -y --no-install-recommends \
    python3-pyqt6 \
    2>/dev/null || true

# Try QScintilla
sudo apt install -y --no-install-recommends \
    python3-pyqt6.qsci \
    2>/dev/null || warn "  python3-pyqt6.qsci khong co, se cai qua pip"

# Qt6 system libs (for pip-installed PyQt6 fallback)
sudo apt install -y --no-install-recommends \
    libqt6widgets6 libqt6gui6 libqt6core6 \
    libgl1-mesa-dev libgles2-mesa-dev libegl1-mesa-dev \
    libxcb-xinerama0 libxcb-cursor0 \
    2>/dev/null || true

# Display server
sudo apt install -y --no-install-recommends \
    xorg x11-xserver-utils \
    2>/dev/null || true

# SQLite + Fonts
sudo apt install -y --no-install-recommends \
    libsqlite3-dev fonts-dejavu-core fontconfig \
    2>/dev/null || true

# ============================================================
# Step 3: Copy source code
# ============================================================
log "[3/7] Copy source code..."

sudo mkdir -p "$INSTALL_DIR"
sudo chown "$USER:$USER" "$INSTALL_DIR"

# Copy source
rsync -a --exclude='.git' --exclude='venv' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='.mypy_cache' --exclude='.pytest_cache' \
    "$SOURCE_DIR/" "$INSTALL_DIR/"

log "  Source copied to $INSTALL_DIR"
log "  Size: $(du -sh "$INSTALL_DIR" | cut -f1)"

# ============================================================
# Step 4: Virtual environment + dependencies
# ============================================================
log "[4/7] Tao virtualenv va cai dependencies..."

cd "$INSTALL_DIR"
$PYTHON_CMD -m venv venv --system-site-packages

source venv/bin/activate

pip install --no-cache-dir --upgrade pip wheel setuptools 2>&1 | tail -1

# Check if system PyQt6 works
SYSTEM_PYQT=false
if python3 -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null; then
    SYSTEM_PYQT=true
    log "  System PyQt6: OK"
fi

# Install dependencies
if [[ "$SYSTEM_PYQT" == "true" ]]; then
    # Only install non-Qt deps
    pip install --no-cache-dir \
        jedi>=0.19.0 pyflakes>=3.1.0 markdown>=3.5 ollama>=0.3.0 \
        2>&1 | tail -3
else
    # Install everything including PyQt6
    warn "  System PyQt6 khong co, cai qua pip (co the mat 5-10 phut)..."
    pip install --no-cache-dir -r requirements.txt 2>&1 | tail -5
fi

# Install app
pip install --no-cache-dir -e . 2>&1 | tail -1

log "  Venv size: $(du -sh venv | cut -f1)"

# ============================================================
# Step 5: Config for ARM / low RAM
# ============================================================
log "[5/7] Tao config cho ARM..."

mkdir -p ~/.neo_code
cat > ~/.neo_code/config.toml << 'CONFIG_EOF'
[application]
language = "vi"

[editor]
font_family = "DejaVu Sans Mono"
font_size = 13

[editor.analysis]
debounce_ms = 1000
max_analysis_time_ms = 3000

[execution]
timeout_seconds = 60
max_memory_mb = 128
max_turtle_commands = 10000
max_robot_commands = 5000

[ai]
provider = "offline"
enable_auto_analysis = false
auto_cooldown_seconds = 30

[ui]
splitter_ratio = [65, 35]
window_width = 1024
window_height = 600

[robot_arena]
simulation_fps = 20

[hardware]
enable_gpio = false
CONFIG_EOF

log "  Config: ~/.neo_code/config.toml"

# ============================================================
# Step 6: Launcher scripts
# ============================================================
log "[6/7] Tao launcher..."

cat > "$INSTALL_DIR/run.sh" << 'RUN_EOF'
#!/bin/bash
export DISPLAY=${DISPLAY:-:0}
export QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-xcb}
export PYTHONPATH=/opt/neo-code/src
source /opt/neo-code/venv/bin/activate
cd /opt/neo-code
exec python3 -m neo_code "$@"
RUN_EOF
chmod +x "$INSTALL_DIR/run.sh"

# Desktop entry
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/neo-code.desktop << 'DESKTOP_EOF'
[Desktop Entry]
Type=Application
Name=NEO CODE
Comment=Educational Python IDE for STEM/Robotics
Exec=/opt/neo-code/run.sh
Terminal=false
Categories=Education;Development;
StartupWMClass=neo-code
DESKTOP_EOF

# Symlink in PATH
sudo ln -sf "$INSTALL_DIR/run.sh" /usr/local/bin/neo-code 2>/dev/null || true

# ============================================================
# Step 7: Verification
# ============================================================
log "[7/7] Kiem tra..."

echo ""
ERRORS=0

# Test imports
if PYTHONPATH="$INSTALL_DIR/src" python3 -c "
from neo_code.core.robot_models import MissionObjective, FieldMission
from neo_code.education.robot_challenges import get_all_field_configs
from neo_code.education.projects import get_projects_by_category
configs = get_all_field_configs()
cats = get_projects_by_category()
total = sum(len(p) for p in cats.values())
print(f'  Modules: OK ({len(configs)} fields, {total} projects)')
" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} Module imports"
else
    echo -e "${RED}[FAIL]${NC} Module imports"
    ERRORS=$((ERRORS+1))
fi

# Test PyQt6
if python3 -c "from PyQt6.QtWidgets import QApplication; print('  PyQt6: OK')" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} PyQt6"
else
    echo -e "${RED}[FAIL]${NC} PyQt6 - can cai them: sudo apt install python3-pyqt6"
    ERRORS=$((ERRORS+1))
fi

# Test dependencies
if python3 -c "import jedi, pyflakes, markdown; print('  Dependencies: OK')" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} Dependencies"
else
    echo -e "${RED}[FAIL]${NC} Dependencies"
    ERRORS=$((ERRORS+1))
fi

# Disk usage
TOTAL_SIZE=$(du -sh "$INSTALL_DIR" | cut -f1)
VENV_SIZE=$(du -sh "$INSTALL_DIR/venv" 2>/dev/null | cut -f1)

echo ""
echo "============================================================"
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN} CAI DAT THANH CONG!${NC}"
else
    echo -e "${YELLOW} Cai dat xong voi $ERRORS loi. Kiem tra lai.${NC}"
fi
echo ""
echo " Install dir:  $INSTALL_DIR"
echo " Total size:   $TOTAL_SIZE"
echo " Venv size:    $VENV_SIZE"
echo " Config:       ~/.neo_code/config.toml"
echo ""
echo " Chay app:"
echo "   neo-code          # Tu terminal"
echo "   /opt/neo-code/run.sh   # Truc tiep"
echo ""
echo " Go cai dat:"
echo "   sudo rm -rf $INSTALL_DIR"
echo "   rm ~/.local/share/applications/neo-code.desktop"
echo "   rm ~/.neo_code/config.toml"
echo "   sudo rm /usr/local/bin/neo-code"
echo "============================================================"

deactivate 2>/dev/null || true
exit $ERRORS
