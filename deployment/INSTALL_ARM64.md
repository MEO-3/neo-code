# NEO CODE - Cai dat tren Linux ARM64

**Target:** ARM Cortex-A53 | RAM 2GB | eMMC 16GB
**OS khuyen nghi:** Debian 12 (Bookworm) / Ubuntu 22.04+ aarch64
**Thoi gian:** ~30 phut

---

## Checklist tong quan

| # | Buoc | Thoi gian | Dung luong |
|---|------|-----------|------------|
| 1 | Chuan bi OS & swap | 5 phut | ~200MB |
| 2 | Cai system packages | 10 phut | ~800MB |
| 3 | Cai Python 3.11+ | 2 phut | co san |
| 4 | Tao virtualenv & cai pip deps | 10 phut | ~600MB |
| 5 | Cau hinh cho ARM/RAM thap | 3 phut | - |
| 6 | Cai font & assets | 1 phut | ~20MB |
| 7 | Tao autostart (tuy chon) | 2 phut | - |
| 8 | Kiem tra | 2 phut | - |
| **Tong** | | **~35 phut** | **~1.6GB** |

> Sau cai dat: ~3GB da dung (OS + app). Con ~12GB cho du lieu.

---

## 1. Chuan bi OS & Swap (ZRAM)

```bash
# === Cap nhat he thong ===
sudo apt update && sudo apt upgrade -y

# === Kiem tra architecture ===
uname -m
# Ket qua phai la: aarch64

# === ZRAM swap (nen trong RAM, KHONG ghi flash - bao ve eMMC) ===
sudo apt install -y zram-tools
cat | sudo tee /etc/default/zramswap << 'EOF'
ALGO=zstd
PERCENT=50
PRIORITY=100
EOF
sudo systemctl enable zramswap
sudo systemctl start zramswap

# === Toi uu cho RAM thap ===
sudo sysctl vm.swappiness=60
echo 'vm.swappiness=60' | sudo tee -a /etc/sysctl.conf

# === Bao ve eMMC: tmpfs + noatime ===
echo 'tmpfs /tmp tmpfs defaults,noatime,size=128M 0 0' | sudo tee -a /etc/fstab
echo 'tmpfs /var/log tmpfs defaults,noatime,size=32M 0 0' | sudo tee -a /etc/fstab
sudo sed -i 's/defaults/defaults,noatime/' /etc/fstab

# === Giam journald ===
sudo mkdir -p /etc/systemd/journald.conf.d
cat | sudo tee /etc/systemd/journald.conf.d/size.conf << 'EOF'
[Journal]
Storage=volatile
RuntimeMaxUse=16M
EOF

# === Kiem tra ===
free -h
# Phai thay: Swap ~1.0G (zram)
```

**Checklist:**
- [ ] `uname -m` = `aarch64`
- [ ] `swapon --show` hien /dev/zram (KHONG phai /swapfile)
- [ ] `mount | grep tmpfs` thay /tmp va /var/log
- [ ] `free -h` hien Swap: ~1.0G

---

## 2. Cai system packages

```bash
# === Build tools ===
sudo apt install -y \
    build-essential \
    pkg-config \
    cmake

# === Python dev headers ===
sudo apt install -y \
    python3-dev \
    python3-venv \
    python3-pip

# === Qt6 system libraries (QUAN TRONG cho ARM) ===
# Cai tu system repo de tranh build tu source (rat cham tren ARM)
sudo apt install -y \
    qt6-base-dev \
    libqt6widgets6 \
    libqt6gui6 \
    libqt6core6 \
    libqt6opengl6-dev \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libegl1-mesa-dev

# === Display server ===
sudo apt install -y \
    xorg \
    x11-xserver-utils

# === SQLite (cho storage) ===
sudo apt install -y libsqlite3-dev

# === Fonts ===
sudo apt install -y \
    fonts-dejavu-core \
    fontconfig
```

**Neu Debian 12 khong co Qt6 packages:**
```bash
# Fallback: cai system PyQt6 tu Debian repo
sudo apt install -y python3-pyqt6 python3-pyqt6.qsci
```

**Checklist:**
- [ ] `python3 --version` >= 3.11
- [ ] `dpkg -l | grep qt6-base` co ket qua
- [ ] `dpkg -l | grep libgl` co ket qua

---

## 3. Kiem tra Python version

```bash
python3 --version
# Can: Python 3.11+

# Neu < 3.11 (vd Ubuntu 22.04 co 3.10):
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-dev python3.11-venv
# Dung python3.11 thay cho python3 o cac buoc sau
```

**Checklist:**
- [ ] Python >= 3.11 da co

---

## 4. Tao virtualenv & cai dependencies

```bash
# === Tao thu muc app ===
sudo mkdir -p /opt/neo-code
sudo chown $USER:$USER /opt/neo-code

# === Copy source code ===
cp -r /duong-dan-source/NEO_CODE/* /opt/neo-code/

# === Tao virtualenv ===
cd /opt/neo-code
python3 -m venv venv --system-site-packages
# --system-site-packages: dung PyQt6 tu system neu co (tiet kiem RAM khi build)

source venv/bin/activate

# === Cai dependencies ===
pip install --upgrade pip wheel setuptools

# Cach 1: Cai tu requirements.txt
pip install -r requirements.txt

# Cach 2: Neu PyQt6 fail tren ARM (thuong gap)
# -> Dung system PyQt6, chi cai phan con lai
pip install jedi>=0.19.0 pyflakes>=3.1.0 markdown>=3.5 ollama>=0.3.0

# === Cai app ===
pip install -e .

# === (Tuy chon) Cai IoT support ===
# Chi can neu dung GPIO/I2C
# pip install gpiozero>=2.0 smbus2>=0.4.0
```

**Xu ly loi thuong gap tren ARM:**

| Loi | Nguyen nhan | Cach xu ly |
|-----|-------------|------------|
| `PyQt6` build fail | Khong du RAM | Dung `--system-site-packages` + `sudo apt install python3-pyqt6` |
| `QScintilla` build fail | Can sip + Qt headers | `pip install PyQt6-QScintilla` hoac `sudo apt install python3-pyqt6.qsci` |
| `Killed` khi pip install | OOM (het RAM) | Bat swap truoc; `pip install --no-cache-dir` |
| `No module named _tkinter` | Khong can (khong dung tkinter) | Bo qua |

**Checklist:**
- [ ] `source /opt/neo-code/venv/bin/activate` khong loi
- [ ] `python3 -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"` thanh cong
- [ ] `python3 -c "import jedi, pyflakes, markdown; print('Deps OK')"` thanh cong
- [ ] `python3 -c "from neo_code.app import main; print('App OK')"` thanh cong

---

## 5. Cau hinh cho ARM / RAM thap

```bash
# === Tao config user ===
mkdir -p ~/.neo_code
cat > ~/.neo_code/config.toml << 'EOF'
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
# Doi sang "gemini" neu co internet + API key:
# provider = "gemini"
# Dat key: export GEMINI_API_KEY="your-key"
#
# Doi sang "ollama" neu chay local LLM:
# provider = "ollama"
# ollama_host = "http://localhost:11434"
# model = "tinyllama"

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
EOF
```

**Toi uu quan trong cho 2GB RAM:**

| Thong so | Mac dinh | ARM 2GB | Ly do |
|----------|----------|---------|-------|
| `max_memory_mb` | 256 | **128** | Giam RAM cho child process |
| `max_turtle_commands` | 50000 | **10000** | Giam buffer |
| `max_robot_commands` | 10000 | **5000** | Giam buffer |
| `simulation_fps` | 30 | **20** | Giam CPU load |
| `enable_auto_analysis` | true | **false** | Tat phan tich tu dong (tiet kiem CPU) |
| `debounce_ms` | 500 | **1000** | Giam tan suat analysis |
| `ai.provider` | gemini | **offline** | Khong can mang, tiet kiem RAM |

**Checklist:**
- [ ] File `~/.neo_code/config.toml` da tao
- [ ] `max_memory_mb = 128`
- [ ] `simulation_fps = 20`

---

## 6. Cai font JetBrains Mono (tuy chon)

```bash
# Font mac dinh: DejaVu Sans Mono (da co tu buoc 2)
# Neu muon dung JetBrains Mono (dep hon):

mkdir -p ~/.local/share/fonts
cd /tmp
wget https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip
unzip JetBrainsMono-2.304.zip -d jetbrains-mono
cp jetbrains-mono/fonts/ttf/*.ttf ~/.local/share/fonts/
fc-cache -fv

# Roi doi config:
# font_family = "JetBrains Mono"
```

**Checklist:**
- [ ] `fc-list | grep -i "dejavu"` co ket qua (bat buoc)
- [ ] `fc-list | grep -i "jetbrains"` (tuy chon)

---

## 7. Tao launcher & autostart

### 7a. Script chay app

```bash
cat > /opt/neo-code/run.sh << 'EOF'
#!/bin/bash
export DISPLAY=:0
export QT_QPA_PLATFORM=xcb
# export QT_QPA_PLATFORM=eglfs    # Dung neu khong co X11 (fullscreen)
# export QT_QPA_PLATFORM=linuxfb  # Dung neu khong co X11/EGL

export PYTHONPATH=/opt/neo-code/src
source /opt/neo-code/venv/bin/activate

cd /opt/neo-code
exec python3 -m neo_code
EOF

chmod +x /opt/neo-code/run.sh
```

### 7b. Desktop entry (cho DE co menu)

```bash
cat > ~/.local/share/applications/neo-code.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=NEO CODE
Comment=Educational Python IDE
Exec=/opt/neo-code/run.sh
Icon=/opt/neo-code/assets/icon.png
Terminal=false
Categories=Education;Development;
EOF
```

### 7c. Autostart khi boot (tuy chon - cho kiosk mode)

```bash
# Cach 1: Systemd user service
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/neo-code.service << 'EOF'
[Unit]
Description=NEO CODE Educational IDE
After=graphical-session.target

[Service]
ExecStart=/opt/neo-code/run.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user enable neo-code
systemctl --user start neo-code

# Cach 2: Autostart don gian (LXDE/Openbox)
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/neo-code.desktop ~/.config/autostart/
```

**Checklist:**
- [ ] `/opt/neo-code/run.sh` chay duoc
- [ ] Autostart da cau hinh (neu can)

---

## 8. Kiem tra cuoi cung

```bash
# === Test 1: Import modules ===
cd /opt/neo-code
source venv/bin/activate
PYTHONPATH=src python3 -c "
from neo_code.core.robot_models import MissionObjective, FieldMission
from neo_code.education.robot_challenges import get_all_field_configs
from neo_code.education.projects import get_projects_by_category
configs = get_all_field_configs()
cats = get_projects_by_category()
total = sum(len(p) for p in cats.values())
print(f'OK: {len(configs)} fields, {total} projects')
"
# Ket qua mong doi: OK: 10 fields, 16 projects

# === Test 2: Chay app ===
/opt/neo-code/run.sh
# App phai hien cua so chinh

# === Test 3: Kiem tra RAM usage ===
# Trong khi app dang chay:
ps aux | grep neo_code | grep -v grep | awk '{print $6/1024 " MB"}'
# Mong doi: < 300MB

# === Test 4: Chuc nang Robot Arena ===
# Trong app: Samples -> "San tap: Di chuyen & Nhat do"
# -> Arena hien san 3000x3000
# -> Co ban do trong code, mission panel, grab range
# -> Bam Run -> robot di chuyen, hien feedback popups
```

**Checklist cuoi:**
- [ ] `10 fields, 16 projects` hien dung
- [ ] App khoi dong khong loi
- [ ] RAM < 300MB khi chay
- [ ] Robot Arena hoat dong
- [ ] Code editor go duoc, co syntax highlight
- [ ] Bam Run chay duoc code Python

---

## Tong dung luong du kien

| Thanh phan | Dung luong |
|------------|------------|
| OS (Debian minimal) | ~1.5 GB |
| System packages (Qt6, dev tools) | ~800 MB |
| Python venv + dependencies | ~600 MB |
| NEO CODE source | ~5 MB |
| ZRAM swap | **0 GB** (nen trong RAM, khong dung flash) |
| Font + assets | ~20 MB |
| **Tong** | **~3 GB** |
| **Con lai (16GB eMMC)** | **~13 GB** |

> ZRAM thay swap file: tiet kiem 1GB flash VA bao ve tuoi tho eMMC.
> Xem chi tiet tai `deployment/OPTIMIZE_FLASH.md`.

---

## Troubleshooting

| Van de | Cach xu ly |
|--------|-----------|
| `Could not load the Qt platform plugin "xcb"` | `sudo apt install libxcb-xinerama0 libxcb-cursor0` |
| App bi cham/lag | Giam `simulation_fps = 15`, tat auto_analysis |
| `Killed` khi chay | Het RAM - kiem tra swap: `swapon --show` |
| Man hinh trang khi khoi dong | `export QT_QPA_PLATFORM=xcb` hoac `eglfs` |
| Font bi vo | Cai `fonts-dejavu-core`, chay `fc-cache -fv` |
| PyQt6 import loi | Dung system package: `sudo apt install python3-pyqt6` |
| Khong co mang cho AI | Dat `provider = "offline"` trong config.toml |
| GPIO permission denied | `sudo usermod -aG gpio $USER` + reboot |

---

## Cau hinh AI (tuy chon)

### Offline (mac dinh - khuyen nghi cho ARM)
Khong can mang. App dung rule-based hints.

### Gemini API (can internet)
```bash
export GEMINI_API_KEY="your-api-key-here"
# Doi config: provider = "gemini"
```

### Ollama local (can RAM >= 4GB - KHONG KHUYEN NGHI cho 2GB)
```bash
# Chi dung neu co RAM > 4GB
curl -fsSL https://ollama.com/install.sh | sh
ollama pull tinyllama
# Doi config: provider = "ollama", model = "tinyllama"
```
