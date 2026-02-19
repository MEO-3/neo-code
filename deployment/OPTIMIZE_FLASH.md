# NEO CODE - Toi uu Flash & So sanh ung dung tuong tu

**Target:** ARM Cortex-A53 | RAM 2GB | eMMC 16GB

---

## 1. Phan tich hien trang NEO CODE

### Source code (rat nhe)

| Module | Dung luong | Dong code |
|--------|-----------|-----------|
| `ui/` | 164 KB | ~2800 |
| `education/` | 108 KB | ~1800 |
| `core/` | 68 KB | ~1200 |
| `ai/` | 60 KB | ~1000 |
| `config/` | 16 KB | ~200 |
| `hardware/` | 16 KB | ~200 |
| `storage/` | 16 KB | ~200 |
| `utils/` | 12 KB | ~200 |
| **Tong source** | **~472 KB** | **~10,228** |

> Source code chi 472KB - **khong phai van de**. Van de nam o **dependencies va OS**.

### Phan bo dung luong tren eMMC 16GB (cai dat chuan)

```
eMMC 16GB
├── OS Debian 12 minimal     ~1,500 MB  ██████████░░░░░░  9.4%
├── System packages (Qt6)      ~800 MB  █████░░░░░░░░░░░  5.0%
├── Python venv + pip deps     ~600 MB  ████░░░░░░░░░░░░  3.8%
├── Swap file                ~1,000 MB  ██████░░░░░░░░░░  6.3%
├── NEO CODE source              ~1 MB  ░░░░░░░░░░░░░░░░  0.0%
├── Font + assets               ~20 MB  ░░░░░░░░░░░░░░░░  0.1%
├── Database + user data        ~50 MB  ░░░░░░░░░░░░░░░░  0.3%
├── Con trong                ~12,029 MB  ████████████████ 75.2%
└── Tong                     16,000 MB
```

### Dependency nao chiem nhieu nhat?

| Package | Dung luong pip | Ghi chu |
|---------|---------------|---------|
| PyQt6 | ~150-200 MB | GUI framework - **lon nhat** |
| QScintilla | ~30-50 MB | Code editor widget |
| jedi | ~30 MB | Autocomplete |
| ollama (Python SDK) | ~5 MB | Chi la SDK, khong phai model |
| pyflakes | ~2 MB | Lint |
| markdown | ~2 MB | Render chat |
| **Tong pip deps** | **~250-300 MB** | |

> **PyQt6 chiem 60-70%** tong dung luong dependency.

---

## 2. So sanh voi ung dung tuong tu

### Bang so sanh tong hop

| Tool | Disk | RAM idle | GUI | Python | ARM64 | 2GB RAM | Doi tuong |
|------|------|---------|-----|--------|-------|---------|-----------|
| **IDLE** | 10-15 MB | 25-40 MB | Tkinter | Co san | Yes | OK | Co ban |
| **Geany** | 4-10 MB | 22 MB | GTK3 | Multi | Yes | OK | Dev chung |
| **Thonny** | 30-50 MB | 60-80 MB | Tkinter | 3.7+ | Yes | OK | Hoc sinh |
| **Mu Editor** | 72-200 MB | 100-150 MB | PyQt5 | 3.7+ | Yes | OK | Hoc sinh |
| **NEO CODE** | **~300 MB** | **~200 MB** | **PyQt6** | **3.11+** | **Yes** | **OK** | **STEM/Robot** |
| Code.org | 0 (web) | 150-400 MB | Browser | JS | Yes | Cham | Hoc sinh |
| Scratch 3 | 230-400 MB | 300-500 MB | Electron | Khong | Yes | Cham | Hoc sinh |
| VEXcode web | 0 (web) | 150-300 MB | Browser | C++/Py | Yes | Cham | Robot |
| WPILib | 5-6 GB | 800+ MB | Electron | Java/C++ | Yes | **Khong** | FRC |

### Phan tich chi tiet

```
Dung luong cai dat (MB)
                                                     WPILib
                                                    ~5500 MB
                                                       |
0       100      200      300      400      500     (break)
|--------|--------|--------|--------|--------|--------|
IDLE ██ 15
Geany █ 10
Thonny ████ 50
Mu Editor ████████████████ 200
NEO CODE █████████████████████████ 300  <-- hien tai
Scratch 3 ██████████████████████████████████ 400

RAM khi chay (MB)
0       100      200      300      400      500
|--------|--------|--------|--------|--------|
Geany ██ 22
IDLE ███ 40
Thonny ██████ 80
Mu Editor ████████████ 150
NEO CODE ████████████████ 200  <-- hien tai
Scratch 3 ████████████████████████████████████████ 500
```

### Nhan xet

| | NEO CODE | Thonny | Mu Editor |
|---|---|---|---|
| **Disk** | 300 MB | 50 MB | 200 MB |
| **RAM** | 200 MB | 80 MB | 150 MB |
| **Tinh nang doc dao** | Robot Arena, AI assistant, Mission system | Debugger step-by-step | MicroPython upload |
| **GUI framework** | PyQt6 (nang) | Tkinter (nhe) | PyQt5 (nang) |
| **Ly do nang hon** | Qt6 + QScintilla + AI module | Chi Tkinter | Qt5 + QScintilla |

> NEO CODE nang hon Thonny **6x disk, 2.5x RAM** chu yeu vi **PyQt6 vs Tkinter**.
> Nhung NEO CODE co Robot Arena 2D, AI assistant, Mission system - Thonny khong co.

---

## 3. Cac phuong an toi uu flash

### Phuong an A: Dung system packages thay pip (Khuyen nghi)

**Tiet kiem:** ~150 MB | **Do kho:** Thap | **Rui ro:** Thap

```bash
# Thay vi pip install PyQt6 (~200MB trong venv)
# -> Dung system package (~0MB them vi Qt6 da cai)
sudo apt install -y python3-pyqt6 python3-pyqt6.qsci

# Tao venv voi --system-site-packages
python3 -m venv venv --system-site-packages

# Chi pip install phan con lai
pip install jedi pyflakes markdown ollama
```

| | pip install (chuan) | system packages |
|---|---|---|
| PyQt6 trong venv | ~200 MB | 0 MB (dung system) |
| QScintilla trong venv | ~40 MB | 0 MB (dung system) |
| Cac dep khac | ~60 MB | ~60 MB |
| **Tong venv** | **~300 MB** | **~60 MB** |
| **Tiet kiem** | | **~240 MB** |

**Tong disk sau toi uu:** ~1,560 MB (app + deps) -> ~760 MB

---

### Phuong an B: Minimal OS (Debian netinst / Armbian minimal)

**Tiet kiem:** ~500-800 MB | **Do kho:** Trung binh | **Rui ro:** Thap

| OS | Dung luong | Ghi chu |
|----|-----------|---------|
| Debian 12 Desktop | ~2,500 MB | Co LXDE/XFCE, nhieu app thua |
| Debian 12 Minimal + X11 | ~800 MB | Chi co X server, khong DE |
| Armbian Minimal | ~600 MB | Toi uu cho SBC |
| Alpine Linux | ~130 MB | Cuc nhe, nhung kho cai Qt6 |

```bash
# Debian minimal + chi cai nhung gi can
sudo apt install --no-install-recommends -y \
    xorg xinit openbox \
    python3 python3-venv python3-pyqt6 python3-pyqt6.qsci \
    fonts-dejavu-core

# Autostart NEO CODE trong openbox
echo '/opt/neo-code/run.sh' >> ~/.config/openbox/autostart
```

**Ket qua:**
```
OS minimal + X11:        ~800 MB  (tiet kiem ~700 MB so voi Desktop)
System Qt6 packages:     ~300 MB
Python venv (nhe):        ~60 MB
NEO CODE source:           ~1 MB
Swap:                  ~1,000 MB
Tong:                  ~2,161 MB  (13.5% cua 16GB)
Con trong:            ~13,839 MB  (86.5%)
```

---

### Phuong an C: Read-only rootfs + OverlayFS

**Tiet kiem:** Bao ve flash | **Do kho:** Cao | **Rui ro:** Trung binh

Muc dich: **Keo dai tuoi tho eMMC** va **chong hu hong** khi mat dien.

```
eMMC layout:
├── /           (squashfs, read-only, nen ~40%)  ~1.2 GB
├── /overlay    (ext4, read-write, tmpfs/eMMC)   ~2 GB
├── /swap       (swap partition)                  ~1 GB
└── /data       (ext4, user data)                ~11.8 GB
```

```bash
# === Buoc 1: Tao squashfs rootfs ===
sudo mksquashfs /rootfs /boot/rootfs.squashfs \
    -comp zstd -Xcompression-level 15 \
    -e /swap /data /tmp /var/log

# === Buoc 2: Cau hinh kernel boot voi overlay ===
# Trong /boot/cmdline.txt hoac bootloader config:
# root=/dev/mmcblk0p2 rootfstype=squashfs overlay=tmpfs

# === Buoc 3: Mount overlay cho phan ghi ===
# /etc/fstab:
# tmpfs /overlay tmpfs defaults,size=256M 0 0
# overlay / overlay lowerdir=/,upperdir=/overlay/upper,workdir=/overlay/work 0 0
```

**Hieu qua nen squashfs:**

| | ext4 | squashfs (zstd) | Tiet kiem |
|---|---|---|---|
| OS + packages | ~2,100 MB | ~900 MB | 57% |
| Python venv | ~300 MB | ~120 MB | 60% |
| **Tong rootfs** | **~2,400 MB** | **~1,020 MB** | **~58%** |

**Uu/nhuoc diem:**

| Uu | Nhuoc |
|----|-------|
| Giam dung luong 58% | Phuc tap khi cap nhat app |
| Bao ve khoi ghi lien tuc | Can rebuild squashfs khi update |
| Chong hu hong mat dien | Debug kho hon |
| Boot nhanh hon (nen = doc it hon) | Can hieu Linux sau |

---

### Phuong an D: Loai bo module khong can

**Tiet kiem:** ~20-50 MB | **Do kho:** Thap | **Rui ro:** Thap

```python
# === Neu khong dung AI (offline mode) ===
# Bo: ollama package (~5 MB)
# Bo: openai import trong ai/llm_client.py
# -> Tiet kiem ~5 MB disk, ~30 MB RAM

# === Neu khong dung GPIO/Hardware ===
# Bo: gpiozero, smbus2
# Da la optional, khong anh huong

# === Giam jedi (autocomplete) ===
# jedi ~30 MB, co the thay bang basic completion
# Nhung mat trai nghiem -> KHONG KHUYEN NGHI
```

---

### Phuong an E: PyInstaller / Nuitka (dong goi 1 file)

**Tiet kiem:** ~50-100 MB | **Do kho:** Cao | **Rui ro:** Cao

```bash
# PyInstaller: dong goi app + deps thanh 1 thu muc
pip install pyinstaller
pyinstaller --onedir --name neo-code \
    --hidden-import neo_code \
    src/neo_code/app.py

# Ket qua: dist/neo-code/ ~150-200 MB (thay vi ~350 MB rieng le)
```

| | Rieng le (venv) | PyInstaller |
|---|---|---|
| Dung luong | ~350 MB | ~180 MB |
| Khoi dong | Nhanh | Cham hon (giai nen) |
| Cap nhat | De (pip install) | Phai rebuild |
| Debug | De | Kho |

> **Khong khuyen nghi** cho giai doan dev. Chi dung khi release san pham.

---

## 4. Phuong an khuyen nghi

### Cho moi truong dev / truong hoc (chon A + B)

```
Phuong an A (system packages) + B (minimal OS) = tot nhat

Tong disk:  ~2.2 GB (13.5% cua 16GB)
RAM:        ~180 MB idle
Con trong:  ~12.8 GB cho du lieu hoc sinh
```

| Buoc | Hanh dong | Tiet kiem |
|------|-----------|-----------|
| 1 | Dung Debian Minimal + Openbox thay Desktop | ~700 MB |
| 2 | `--system-site-packages` + system PyQt6 | ~240 MB |
| 3 | `--no-install-recommends` cho apt | ~100 MB |
| 4 | Tat AI (provider = "offline") | ~30 MB RAM |
| **Tong tiet kiem** | | **~1,040 MB disk** |

### Cho san pham / kiosk (chon A + B + C)

```
Them squashfs overlay = bao ve flash + nho hon nua

Tong disk:  ~1.0 GB rootfs (nen)
            + 2 GB overlay + data
            + 1 GB swap
            = ~4 GB
Con trong:  ~12 GB cho du lieu
Tuoi tho eMMC: tang ~3-5x (it ghi hon)
```

---

## 5. Lenh thuc hien nhanh (Phuong an A)

```bash
# === Tren thiet bi ARM64 ===

# 1. System PyQt6 (thay vi pip)
sudo apt install --no-install-recommends -y \
    python3-pyqt6 python3-pyqt6.qsci

# 2. Venv nhe
cd /opt/neo-code
python3 -m venv venv --system-site-packages
source venv/bin/activate

# 3. Chi cai deps nhe
pip install --no-cache-dir jedi pyflakes markdown ollama

# 4. Cai app
pip install --no-cache-dir -e .

# 5. Kiem tra dung luong
du -sh venv/          # Mong doi: ~60-80 MB (thay vi ~300 MB)
du -sh /opt/neo-code/ # Mong doi: ~70-90 MB tong

# 6. Don dep
sudo apt clean
pip cache purge
rm -rf /tmp/*
```

---

## 6. So sanh tong hop cac phuong an

```
Dung luong tong (OS + App) tren eMMC 16GB:

                            0     1     2     3     4     5 GB
                            |-----|-----|-----|-----|-----|
Cai dat chuan:              ████████████████████  3.9 GB
                            [OS 1.5][Qt.8][venv.6][swap 1]

A: System packages:         ███████████████░░░░░  3.1 GB  (-20%)
                            [OS 1.5][Qt.8][v.06][swap 1]

A+B: Minimal OS:            ████████████░░░░░░░░  2.2 GB  (-44%)
                            [OS.8][Qt.3][v.06][swap 1]

A+B+C: Squashfs:            ████████░░░░░░░░░░░░  1.6 GB  (-59%)
                            [sqsh 1.0][swap 0.6]

Con trong cho du lieu:
  Chuan:                    ████████████░░░░░░░░  12.1 GB
  Phuong an A+B:            ██████████████░░░░░░  13.8 GB  (+14%)
  Phuong an A+B+C:          ██████████████████░░  14.4 GB  (+19%)
```
