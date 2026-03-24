# 🤖 Robot Feature — Architecture & Implementation Spec

## Overview

The **Robot Feature** integrates [thingbot-telemetrix](https://github.com/MEO-3/thingbot-telemetrix) into NEO Code, giving students structured missions to control real hardware (LEDs, motors, servos, buzzers, switches) via USB from their Python code.

It follows the same `IFeature` pattern as the Lesson Feature: mission browser sidebar → workspace panel → student edits real code in the IDE editor → runs via existing `QProcess` runner.

---

## 🎯 Goals

- Teach hardware Python programming through guided, hands-on missions
- Use the **real** `thingbot-telemetrix` API (no fake wrappers)
- Keep the IDE architecture stable — no new core signals, no new execution path
- Let the existing `QProcess` runner own the serial port (no conflicts)

---

## 🧱 Tech Stack Addition

| Concern | Choice |
|---|---|
| Hardware library | `thingbot-telemetrix` (install from GitHub) |
| Serial communication | Handled inside student's `QProcess` subprocess |
| Port detection | `glob` on `/dev/ttyUSB*`, `/dev/ttyACM*` |

### Dependency (pyproject.toml)

```toml
[project.optional-dependencies]
robot = [
    "thingbot-telemetrix @ git+https://github.com/MEO-3/thingbot-telemetrix.git",
]
```

Use optional so ARM/x86 dev machines without hardware can still run the IDE.

---

## 🔌 thingbot-telemetrix API Reference

```python
from thingbot_telemetrix import Telemetrix
from thingbot_telemetrix.private_constants import ThingBot

board = Telemetrix()                                    # auto-detect USB port

# LED  (brightness 0–100)
board.thingbot().control_led(ThingBot.LED_1, 100)      # on
board.thingbot().control_led(ThingBot.LED_1, 0)        # off

# DC Motor  (speed -255..255, negative = reverse)
board.thingbot().control_dc(ThingBot.MOTOR_1, 200)     # forward
board.thingbot().control_dc(ThingBot.MOTOR_1, -200)    # backward
board.thingbot().control_dc(ThingBot.MOTOR_1, 0)       # stop

# Servo  (angle 0–180)
board.thingbot().control_servo(ThingBot.SERVO_1, 90)

# Buzzer  (frequency Hz, 0 = off)
board.thingbot().control_buzzer(440)
board.thingbot().control_buzzer(0)

# Switch callback
board.thingbot().set_sw_callback(lambda state: print("pressed" if state else "released"))

# GPIO (raw pins)
board.gpio().set_pin_mode_output(7)
board.gpio().digital_write(7, 1)

board.shutdown()
```

### ThingBot Hardware Constants

| Constant | Value | Type |
|---|---|---|
| `LED_1`, `LED_2` | 1, 2 | LED |
| `MOTOR_1`–`MOTOR_4` | 1–4 | DC Motor |
| `SERVO_1`–`SERVO_5` | 1–5 | Servo |

---

## 🗂️ Mission Structure

```
Module → Mission
```

Stored in `features/robot/data/robot_pack.json`.

Each mission has:

| Field | Description |
|---|---|
| `id` | Unique string identifier |
| `title` | Display name in sidebar |
| `goal` | What the student must achieve |
| `api_hint` | Relevant API snippet shown in workspace |
| `starter_code` | Real working thingbot-telemetrix Python code |

### Curriculum (robot_pack.json)

| Module | Missions |
|---|---|
| ThingBot Cơ bản | Nháy LED, Di chuyển tiến |
| Servo & Còi | Quay Servo, Kêu Còi |
| Nút Nhấn | Phản hồi nút nhấn |

---

## 🏗️ Architecture

### Key Design Decision: QProcess Owns the Serial Port

The IDE **never** holds a `Telemetrix()` connection. Student code runs in a `QProcess` subprocess that exclusively owns the serial port. This avoids:
- Two processes competing for the same `/dev/ttyUSB0`
- Telemetrix's internal thread conflicting with Qt's event loop
- Blocking the UI during hardware initialization

```
[IDE process]                    [QProcess subprocess]
  RobotFeature                     student_script.py
  port scanner only                  Telemetrix()  ←── serial port
  shows port hint                    board.thingbot().control_led(...)
                                     board.shutdown()
        stdout/stderr ───────────────────────────────► TerminalPanel
```

### Execution Flow

```
[Sidebar] Select mission
    ↓
[Workspace] goal + api_hint + starter_code shown
    ↓
"Nạp mã mẫu" → event_bus.project_opened(starter_code) → editor filled
    ↓
Student edits code → clicks Run (F5)
    ↓
execution_requested(code) → runner.py → QProcess("python3 temp.py")
    ↓
stdout → stdout_received → TerminalPanel
stderr → stderr_received → TerminalPanel
    ↓
QProcess exits → execution_finished(exit_code)
```

No new EventBus signals. No new execution path. Identical to regular script mode.

---

## 📁 Folder Structure

```
features/robot/
  __init__.py
  feature.py              # RobotFeature(IFeature) — wires panel + connect handler
  robot_panel.py          # QStackedWidget: sidebar list ↔ workspace detail
  robot_sidebar.py        # QTreeWidget mission browser (Module → Mission)
  robot_workspace.py      # Goal / API hint / starter code / buttons
  robot_connection.py     # NEW: find_serial_ports() helper
  loader.py               # load_robot_pack() → dict from JSON
  data/
    robot_pack.json       # Mission content with real thingbot-telemetrix code
```

---

## 🔧 Component Responsibilities

### `feature.py` — `RobotFeature(IFeature)`

- Instantiates `RobotPanel` on `activate()`
- Connects `connect_requested` → `_on_connect()` which calls `find_serial_ports()` and updates status label
- Returns `RobotPanel` as sidebar widget

### `robot_connection.py` — Port Scanner

```python
import glob

def find_serial_ports() -> list[str]:
    return sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
```

Lightweight. No serial connection held. Just locates the device so the status label can guide the student.

### `robot_workspace.py` — Workspace Panel

Displays for the selected mission:
- **🎯 Mục tiêu** — `goal` text
- **🧪 API** — `api_hint` code snippet
- **🧩 Mã mẫu** — read-only `starter_code` preview
- **"Nạp mã mẫu"** button → emits `project_opened` via EventBus → fills editor
- **"Kết nối USB"** button → calls `find_serial_ports()` → updates status label
- **Status label** — shows port info or "not connected" hint

### `robot_sidebar.py` — Mission Browser

`QTreeWidget` with non-selectable module headers and selectable mission rows. Emits `mission_selected(dict)` on click.

### `robot_panel.py` — Panel Orchestrator

`QStackedWidget` toggling between sidebar list and workspace detail. Exposes `set_status()` for the feature to push connection state.

---

## ⚠️ UX Notes

- "Kết nối USB" does **not** open a connection — it scans ports and reports what it finds
- Students are guided to call `Telemetrix()` in their own code (starter code already does this)
- If no board is found, status shows: `❌ Không tìm thấy board. Kiểm tra cáp USB.`
- If board found: `✅ Board: /dev/ttyUSB0 — Nhấn Run để chạy code!`
- Telemetrix logs appear in TerminalPanel as stderr (expected behavior, not an error)

---

## 📋 Changes Summary

| File | Status | Change |
|---|---|---|
| `pyproject.toml` | Modify | Add `thingbot-telemetrix` as optional `robot` dependency |
| `features/robot/data/robot_pack.json` | Modify | Replace mock APIs with real thingbot-telemetrix `starter_code` |
| `features/robot/robot_connection.py` | **New** | `find_serial_ports()` helper |
| `features/robot/feature.py` | Modify | Wire `connect_requested` → port scan + status update |
| `features/robot/robot_workspace.py` | Modify | "Kết nối USB" calls port scan; display status result |
| `features/robot/robot_sidebar.py` | No change | Already correct |
| `features/robot/robot_panel.py` | No change | Already correct |
| `features/robot/loader.py` | No change | Already correct |
| `core/`, `ui/`, `execution/` | No change | Architecture unchanged |
