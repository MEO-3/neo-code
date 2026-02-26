# NEO CODE - Tai lieu Kien truc Phan mem

> **Phien ban:** 0.1.0 (Alpha)
> **Ngon ngu:** Python 3.11+ | PyQt6
> **Giay phep:** GPL-3.0-or-later
> **Ngay cap nhat:** 2026-02-26

---

## 1. TONG QUAN

**NEO CODE** la mot IDE (Moi truong Phat trien Tich hop) giao duc danh cho hoc sinh STEM/Robotics. Phan mem giup hoc sinh hoc lap trinh Python thong qua cac du an truc quan (Turtle Graphics, Robot Arena) voi su ho tro cua tro ly AI.

**Doi tuong su dung:** Hoc sinh tu 6-12 tuoi
**Ngon ngu giao dien:** Tieng Viet (chinh) + Tieng Anh

---

## 2. TECHNOLOGY STACK

| Thanh phan | Cong nghe | Phien ban |
|------------|-----------|-----------|
| GUI Framework | PyQt6 | 6.5.0+ |
| Code Editor | QScintilla | 2.14.0+ |
| Code Completion | Jedi | 0.19.0+ |
| Static Analysis | PyFlakes | 3.1.0+ |
| AI (Cloud) | Gemini API (OpenAI-compatible) | gemini-2.5-flash |
| AI (Local) | Ollama | 0.3.0+ |
| Markdown | markdown | 3.5+ |
| Hardware (optional) | gpiozero, smbus2 | 2.0+, 0.4.0+ |
| Database | SQLite3 | Built-in |
| Testing | pytest, pytest-qt | 7.4.0+, 4.2.0+ |
| Linting | ruff, mypy | 0.1.0+, 1.6.0+ |

---

## 3. KIEN TRUC TONG THE (Layered Architecture)

```
+================================================================+
|                                                                  |
|                    UI LAYER (PyQt6)                              |
|                                                                  |
|  +------------+  +--------------+  +-------------+              |
|  | MainWindow |  | CodeEditor   |  | EditorTool- |              |
|  | (Split     |  | (QScintilla  |  | bar (Run,   |              |
|  |  Layout)   |  |  Syntax HL)  |  |  Stop, Save)|              |
|  +------------+  +--------------+  +-------------+              |
|                                                                  |
|  +------------+  +--------------+  +-------------+              |
|  | Turtle     |  | Robot Arena  |  | AI Chat     |              |
|  | Canvas     |  | Canvas       |  | Panel       |              |
|  | (QPainter) |  | (QPainter)   |  | (Markdown)  |              |
|  +------------+  +--------------+  +-------------+              |
|                                                                  |
|  +------------+  +--------------+  +-------------+              |
|  | Output     |  | Progress     |  | Level       |              |
|  | Panel      |  | Widget       |  | Selector    |              |
|  +------------+  +--------------+  +-------------+              |
|                                                                  |
+==========================+=======================================+
                           |
                     SignalBus (Qt Signals)
                           |
+==========================v=======================================+
|                                                                  |
|                APPLICATION LAYER (Services)                      |
|                                                                  |
|  +--------------------+  +-------------------+                   |
|  | AI Assistant       |  | Execution         |                   |
|  | Service            |  | Worker            |                   |
|  | (Hint Levels,      |  | (QThread,         |                   |
|  |  Context Builder,  |  |  Subprocess       |                   |
|  |  Conversation)     |  |  Sandbox)         |                   |
|  +--------------------+  +-------------------+                   |
|                                                                  |
|  +--------------------+  +-------------------+                   |
|  | Phase Manager      |  | Progress          |                   |
|  | (Phase 1: Turtle,  |  | Tracker           |                   |
|  |  Phase 2: IoT)     |  | (Skill Level)     |                   |
|  +--------------------+  +-------------------+                   |
|                                                                  |
+==========================+=======================================+
                           |
+==========================v=======================================+
|                                                                  |
|                CORE PROCESSING LAYER                             |
|                                                                  |
|  +--------------------+  +-------------------+                   |
|  | Code Analyzer      |  | Code Completer    |                   |
|  | (AST + PyFlakes)   |  | (Jedi)            |                   |
|  +--------------------+  +-------------------+                   |
|                                                                  |
|  +--------------------+  +-------------------+                   |
|  | Turtle             |  | Robot             |                   |
|  | Interpreter        |  | Interpreter       |                   |
|  | (Command Proxy)    |  | (Command Proxy)   |                   |
|  +--------------------+  +-------------------+                   |
|                                                                  |
|  +--------------------+  +-------------------+                   |
|  | Robot Physics      |  | LLM Client        |                   |
|  | Engine (2D)        |  | (Gemini/Ollama)   |                   |
|  +--------------------+  +-------------------+                   |
|                                                                  |
+==========================+=======================================+
                           |
+==========================v=======================================+
|                                                                  |
|                DATA LAYER                                        |
|                                                                  |
|  +--------------------+  +-------------------+                   |
|  | SQLite Database    |  | Settings          |                   |
|  | (Student Profiles, |  | (TOML Config,     |                   |
|  |  Sessions, Chat)   |  |  Dataclass)       |                   |
|  +--------------------+  +-------------------+                   |
|                                                                  |
|  +--------------------+  +-------------------+                   |
|  | Models             |  | Curriculum Data   |                   |
|  | (Dataclasses)      |  | (Lessons, Projects|                   |
|  +--------------------+  |  Exercises)        |                   |
|                          +-------------------+                   |
|                                                                  |
+================================================================+
```

---

## 4. CAU TRUC THU MUC

```
NEO_CODE/
|
|-- src/neo_code/                    # Source code chinh
|   |-- __init__.py                  # Version: 0.1.0
|   |-- __main__.py                  # Entry point (python -m neo_code)
|   |-- app.py                       # Khoi tao ung dung PyQt6
|   |
|   |-- config/                      # [Quan ly Cau hinh]
|   |   |-- settings.py              # Settings loader (TOML, dataclass)
|   |   +-- defaults.toml            # Gia tri mac dinh
|   |
|   |-- core/                        # [Xu ly Loi - 9 files]
|   |   |-- models.py                # Data models (AnalysisResult, ExecutionResult, AIResponse...)
|   |   |-- code_analyzer.py         # Phan tich code: AST + PyFlakes
|   |   |-- code_completer.py        # Tu dong hoan thanh code: Jedi
|   |   |-- execution_engine.py      # Chay code trong subprocess sandbox
|   |   |-- turtle_interpreter.py    # Chuyen doi lenh Turtle -> DrawCommand
|   |   |-- robot_interpreter.py     # Chuyen doi lenh Robot -> RobotCommand
|   |   |-- robot_models.py          # Models cho Robot Arena (FGC fields)
|   |   +-- robot_physics.py         # Physics engine 2D (va cham, diem so)
|   |
|   |-- ai/                          # [Tro ly AI - 7 files]
|   |   |-- llm_client.py            # Client cho Gemini API + Ollama
|   |   |-- assistant_service.py     # Dieu phoi AI chinh (hint levels)
|   |   |-- context_builder.py       # Xay dung prompt tu code & analysis
|   |   |-- conversation_history.py  # Quan ly lich su hoi thoai
|   |   |-- response_parser.py       # Parse LLM output -> AIResponse
|   |   +-- prompt_templates.py      # System prompts cho tung Phase
|   |
|   |-- education/                   # [Giao duc - 7 files]
|   |   |-- curriculum.py            # Dinh nghia bai hoc (Phase 1 & 2)
|   |   |-- projects.py              # Du an giao duc (3 muc do kho)
|   |   |-- phase_manager.py         # Chuyen doi Phase 1 <-> Phase 2
|   |   |-- progress_tracker.py      # Theo doi tien do hoc sinh
|   |   |-- robot_challenges.py      # Thach thuc Robot FGC
|   |   +-- hints/                   # He thong goi y
|   |       |-- common_errors.py     # Goi y loi pho bien (rule-based)
|   |       +-- turtle_hints.py      # Goi y rieng cho Turtle
|   |
|   |-- ui/                          # [Giao dien - 12 files]
|   |   |-- main_window.py           # Cua so IDE chinh (split layout)
|   |   |-- code_editor.py           # Code editor + syntax highlighting
|   |   |-- editor_toolbar.py        # Toolbar (Run, Stop, Save, Phase...)
|   |   |-- turtle_canvas.py         # Ve Turtle bang QPainter
|   |   |-- robot_arena_canvas.py    # Ve Robot Arena bang QPainter
|   |   |-- ai_chat_panel.py         # Panel chat AI (markdown)
|   |   |-- ai_input_widget.py       # O nhap cau hoi cho AI
|   |   |-- output_panel.py          # Hien thi stdout/stderr
|   |   |-- progress_widget.py       # Hien thi tien do hoc tap
|   |   |-- theme.py                 # Dark theme (Catppuccin)
|   |   |-- samples.py               # Mau code san
|   |   +-- dialogs/
|   |       +-- level_selector.py    # Dialog chon muc do kho
|   |
|   |-- hardware/                    # [Phan cung - 3 files]
|   |   |-- gpio_wrapper.py          # GPIO abstraction (gpiozero/RPi.GPIO)
|   |   |-- sensor_manager.py        # Quan ly cam bien
|   |   +-- simulator.py             # Mo phong phan cung
|   |
|   |-- storage/                     # [Luu tru - 3 files]
|   |   |-- database.py              # SQLite (student profiles, sessions)
|   |   +-- models.py                # ORM-like models
|   |
|   +-- utils/                       # [Tien ich - 3 files]
|       |-- signal_bus.py            # Event hub (Qt Signals)
|       +-- debouncer.py             # Debounce cho code analysis
|
|-- tests/                           # Bo test
|   |-- unit/                        # Unit tests
|   |-- integration/                 # Integration tests
|   +-- e2e/                         # End-to-end tests
|
|-- curriculum_data/                 # Noi dung giao duc
|   |-- phase1/exercises/            # Bai tap Phase 1
|   +-- phase2/exercises/            # Bai tap Phase 2
|
|-- deployment/                      # Trien khai
|   |-- install-arm64.sh             # Cai dat cho Raspberry Pi
|   |-- build-package.sh             # Build ARM64 package
|   +-- requirements-arm64.txt       # Dependencies ARM64
|
|-- DOC/                             # Tai lieu
|-- pyproject.toml                   # Project metadata
|-- requirements.txt                 # Dependencies
+-- Makefile                         # Build commands
```

---

## 5. DESIGN PATTERNS SU DUNG

### 5.1 Signal Bus Pattern (Event-Driven)
Cac component giao tiep thong qua SignalBus trung tam, khong phu thuoc truc tiep.

```
CodeEditor --code_changed--> SignalBus ---> CodeAnalyzer
                                       ---> AIAssistantService
                                       ---> ProgressTracker

ExecutionEngine --stdout_received--> SignalBus ---> OutputPanel
                --draw_command-----> SignalBus ---> TurtleCanvas
                --robot_command----> SignalBus ---> RobotArena
```

**Danh sach Signals:**
| Nhom | Signal | Muc dich |
|------|--------|----------|
| Editor | code_changed, file_opened, file_saved | Thay doi code |
| Execution | execution_started, execution_finished, stdout_received, stderr_received | Chay code |
| Analysis | analysis_complete | Ket qua phan tich |
| AI | ai_thinking, ai_response_chunk, ai_response_complete, ai_error | AI response |
| Canvas | draw_command, canvas_clear, robot_command, arena_clear | Ve do hoa |
| Education | phase_changed, lesson_changed, exercise_loaded, progress_updated | Hoc tap |
| App | settings_changed, status_message | He thong |

### 5.2 Worker Thread Pattern
Cac tac vu nang chay tren QThread rieng de khong block UI:
- **CodeAnalyzerWorker** - Phan tich code nen
- **ExecutionWorker** - Chay subprocess
- **AIQueryWorker** - Goi LLM API

### 5.3 Proxy Pattern (Command Interception)
Code cua hoc sinh dung `turtle` / `robot` binh thuong. He thong inject wrapper code de:
1. Chan lenh goc
2. Chuyen thanh JSON output
3. IDE parse JSON -> render do hoa

```
Hoc sinh viet:    turtle.forward(100)
                       |
Wrapper inject:   -> ghi JSON {"cmd": "forward", "args": [100]} ra stdout
                       |
IDE doc:          -> Parse JSON -> DrawCommand -> TurtleCanvas render
```

### 5.4 Progressive Hint Strategy Pattern
4 muc do goi y tang dan:
```
NUDGE     -> "Hay nghi xem dieu gi xay ra khi..."
GUIDANCE  -> "Van de lien quan den bien vong lap cua ban"
EXPLICIT  -> "Doi dong 5: dung range(4) thay vi range(3)"
SOLUTION  -> Code dap an hoan chinh
```

---

## 6. LUONG DU LIEU CHINH

### 6.1 Luong Chay Code

```
[User nhap code] --> CodeEditor
       |
       v
  code_changed signal --> SignalBus
       |                      |
       v                      v
  CodeAnalyzer           AIAssistantService
  (AST + PyFlakes)       (Auto-analysis)
       |                      |
       v                      v
  analysis_complete      ai_response_complete
       |                      |
       v                      v
  [Error markers]        [Chat panel]

[User nhan Run] --> EditorToolbar
       |
       v
  ExecutionEngine.execute()
       |
       +---> Inject wrapper code (turtle/robot proxy)
       |
       +---> Spawn subprocess (Python)
       |
       +---> Stream stdout/stderr
              |
              +---> Parse JSON commands --> draw_command signal --> TurtleCanvas
              |
              +---> Text output --> stdout_received signal --> OutputPanel
              |
              +---> Ket thuc --> execution_finished signal
```

### 6.2 Luong AI Assistant

```
[Trigger: Code thay doi / User hoi]
       |
       v
  AssistantService.handle_query()
       |
       v
  ContextBuilder.build_context()
       |-- Code hien tai (max 200 dong)
       |-- Ket qua analysis (errors, patterns)
       |-- Student profile (skill level, phase)
       |-- Conversation history (6 turns)
       |
       v
  LLMClient.query()
       |
       +---> Gemini API (Primary)
       |     hoac
       +---> Ollama (Fallback)
       |     hoac
       +---> Offline hints (Rule-based)
       |
       v
  ResponseParser.parse()
       |
       v
  AIResponse {hint_level, message, code_suggestion, explanation}
       |
       v
  ai_response_complete signal --> AIChatPanel
```

### 6.3 Luong Robot Arena

```
[User viet code robot] --> CodeEditor
       |
       v
  ExecutionEngine + RobotInterpreter (proxy inject)
       |
       v
  JSON robot commands (move, grab, release, turn...)
       |
       v
  RobotPhysicsEngine
       |-- Xu ly va cham
       |-- Tinh diem
       |-- Kiem tra mission objectives
       |-- AI robot behavior
       |
       v
  RobotArenaCanvas (QPainter render)
       |-- Grid background
       |-- Game pieces
       |-- Robot trails
       |-- Scoring zones
       +-- Mission progress
```

---

## 7. MO HINH DU LIEU CHINH

### Core Models (`core/models.py`)

```
ErrorSeverity: ERROR | WARNING | INFO | HINT

CodePattern: TURTLE_DRAWING | LOOP_CONSTRUCT | FUNCTION_DEFINITION |
             GPIO_SETUP | SENSOR_READ | ROBOT_PROGRAMMING | ...

CodeError:
  +-- line: int
  +-- column: int
  +-- message: str
  +-- severity: ErrorSeverity
  +-- suggestion: Optional[str]

AnalysisResult:
  +-- errors: List[CodeError]
  +-- patterns: Set[CodePattern]
  +-- imports: List[str]
  +-- functions: List[str]
  +-- variables: List[str]
  +-- complexity: int
  +-- line_count: int

DrawCommand:
  +-- command: str (forward, left, pencolor, ...)
  +-- args: List[Any]

ExecutionResult:
  +-- exit_code: int
  +-- stdout: str
  +-- stderr: str
  +-- execution_time: float
  +-- draw_commands: List[DrawCommand]

HintLevel: NUDGE | GUIDANCE | EXPLICIT | SOLUTION

AIResponse:
  +-- hint_level: HintLevel
  +-- message: str
  +-- code_suggestion: Optional[str]
  +-- explanation: Optional[str]

StudentProfile:
  +-- name: str
  +-- current_phase: int
  +-- current_lesson: int
  +-- skill_level: int (1-5)
  +-- completed_exercises: List[str]
  +-- common_errors: Dict[str, int]
  +-- total_runs: int
  +-- errors_fixed: int
```

### Robot Models (`core/robot_models.py`)

```
RobotCommandType: FORWARD | BACKWARD | TURN_LEFT | TURN_RIGHT |
                  GRAB | RELEASE | SHOOT | DISTANCE_SENSOR | ...

GamePiece:
  +-- id: str
  +-- type: ball | cube | cylinder
  +-- position: (x, y)
  +-- color: str
  +-- points: int

ScoringZone:
  +-- id: str
  +-- bounds: (x, y, w, h)
  +-- multiplier: float
  +-- alliance: str

FieldConfig:
  +-- name: str
  +-- size: (7000, 7000) mm
  +-- pieces: List[GamePiece]
  +-- zones: List[ScoringZone]
  +-- obstacles: List[Obstacle]
  +-- missions: List[FieldMission]
  +-- duration: int (seconds)

RobotState:
  +-- position: (x, y)
  +-- heading: float (degrees)
  +-- holding: Optional[GamePiece]
  +-- score: int
  +-- trail: List[(x, y)]
```

---

## 8. CAU HINH HE THONG

Cau hinh theo thu tu uu tien:
1. **Built-in defaults** (trong code)
2. **User config** (`~/.neo_code/config.toml`)
3. **Environment variables** (runtime)

```
AppSettings:
  |
  |-- editor:
  |     font_family: "JetBrains Mono"
  |     font_size: 14
  |     theme: "dark"
  |     analysis_debounce_ms: 500
  |
  |-- execution:
  |     timeout_seconds: 30
  |     max_memory_mb: 256
  |     turtle_animation_speed: 5
  |     max_commands: 10000
  |
  |-- ai:
  |     provider: "gemini" | "ollama" | "offline"
  |     model: "gemini-2.5-flash"
  |     fallback_model: "gemini-2.0-flash"
  |     temperature: 0.3
  |     max_tokens: 512
  |     auto_analysis_tokens: 200
  |     context_turns: 6
  |     cooldown_seconds: 10
  |
  |-- education:
  |     default_phase: 1
  |     curriculum_path: "./curriculum_data"
  |
  |-- hardware:
  |     gpio_enabled: false
  |     gpio_library: "gpiozero"
  |
  |-- storage:
  |     db_path: "~/.neo_code/data.db"
  |     projects_dir: "~/.neo_code/projects"
  |
  |-- ui:
  |     window_width: 1200
  |     window_height: 800
  |     theme: "catppuccin-dark"
  |
  +-- robot_arena:
        default_field: "training_basic"
        simulation_fps: 30
        difficulty: "normal"
```

---

## 9. PHAN TICH TINH NANG

### 9.1 TINH NANG DA HOAN THANH (Done)

| # | Tinh nang | Mo ta | Files chinh |
|---|-----------|-------|-------------|
| 1 | **Code Editor** | Sua code Python voi syntax highlighting, line numbers, auto-indent | `ui/code_editor.py` |
| 2 | **Code Analysis** | Phat hien loi realtime bang AST + PyFlakes | `core/code_analyzer.py` |
| 3 | **Code Completion** | Tu dong hoan thanh code bang Jedi | `core/code_completer.py` |
| 4 | **Code Execution** | Chay code trong subprocess sandbox, timeout, memory limit | `core/execution_engine.py` |
| 5 | **Turtle Graphics** | Canvas rieng bang QPainter, animation micro-step, KTurtle cursor | `ui/turtle_canvas.py`, `core/turtle_interpreter.py` |
| 6 | **Robot Arena 2D** | Mo phong san FGC, physics, va cham, diem so | `ui/robot_arena_canvas.py`, `core/robot_physics.py` |
| 7 | **AI Assistant (Gemini)** | Tro ly AI tich hop Gemini API, tu dong phan tich code | `ai/assistant_service.py`, `ai/llm_client.py` |
| 8 | **AI Assistant (Ollama)** | Ho tro chay LLM local bang Ollama | `ai/llm_client.py` |
| 9 | **Offline Hints** | Goi y rule-based khi khong co internet | `education/hints/common_errors.py`, `education/hints/turtle_hints.py` |
| 10 | **Progressive Hints** | 4 cap do goi y: NUDGE -> GUIDANCE -> EXPLICIT -> SOLUTION | `ai/assistant_service.py` |
| 11 | **Curriculum Phase 1** | 4 bai hoc: Print, Turtle, Loops, Functions | `education/curriculum.py` |
| 12 | **Project System** | 10 du an giao duc, moi du an 3 muc do kho | `education/projects.py` |
| 13 | **3-Level Difficulty** | Kham Pha (6-8t), Lap Trinh Vien (9-11t), Chuyen Gia (12+) | `education/projects.py`, `ui/dialogs/level_selector.py` |
| 14 | **Student Progress** | Theo doi tien do, skill level 1-5, error patterns | `education/progress_tracker.py` |
| 15 | **Phase Manager** | Chuyen doi Phase 1 (Turtle) <-> Phase 2 (IoT) | `education/phase_manager.py` |
| 16 | **Robot Challenges** | Cau hinh san FGC, mission objectives, AI robot doi thu | `education/robot_challenges.py` |
| 17 | **Dark Theme** | Giao dien toi kieu Catppuccin | `ui/theme.py` |
| 18 | **Bilingual UI** | Ho tro Tieng Viet + Tieng Anh | Toan bo AI prompts + UI messages |
| 19 | **Signal Bus** | He thong event de-coupled giua cac component | `utils/signal_bus.py` |
| 20 | **Output Panel** | Hien thi stdout/stderr realtime | `ui/output_panel.py` |
| 21 | **Conversation History** | Luu lich su hoi thoai AI (6 turns) | `ai/conversation_history.py` |
| 22 | **Context Builder** | Xay dung prompt thong minh tu code + analysis | `ai/context_builder.py` |
| 23 | **Sample Code** | Cac mau code san de hoc sinh bat dau nhanh | `ui/samples.py` |
| 24 | **SQLite Storage** | Luu student profiles, sessions, chat history | `storage/database.py` |
| 25 | **ARM64 Deployment** | Script cai dat + build cho Raspberry Pi | `deployment/` |

### 9.2 TINH NANG DANG PHAT TRIEN / CHUA HOAN THIEN (In Progress)

| # | Tinh nang | Trang thai | Chi tiet |
|---|-----------|------------|----------|
| 1 | **Phase 2: IoT/Hardware** | ~30% | Co GPIO wrapper, sensor manager, simulator nhung chua co bai hoc day du. File `hardware/` co code framework nhung chua tich hop hoan chinh voi UI |
| 2 | **Curriculum Phase 2** | ~20% | Thu muc `curriculum_data/phase2/` da tao nhung noi dung con it. Chi co starter code cho LED blink va button read |
| 3 | **Test Coverage** | ~15% | Cau truc test (unit/integration/e2e) da setup nhung so luong test case con han che |
| 4 | **Robot Arena - Nhieu san** | ~60% | Co 7 cau hinh san FGC (2017-2025) nhung mot so chua hoan thien du lieu |
| 5 | **Hardware Simulator** | ~40% | Framework co nhung chua mo phong day du tat ca cam bien |

### 9.3 TINH NANG CHUA LAM (Planned/TODO)

| # | Tinh nang | Ly do du doan |
|---|-----------|---------------|
| 1 | **Mobile/Tablet Version** | Chua co code Kivy hoac mobile framework |
| 2 | **Python Debugger** | Chua co breakpoint, step-through |
| 3 | **Multiplayer/Collaboration** | Chua co networking code |
| 4 | **Video Tutorial** | Chua co tich hop video |
| 5 | **Performance Profiler** | Chua co profiling tools |
| 6 | **Plugin System** | Kien truc hien tai chua ho tro plugins |
| 7 | **Export/Share Projects** | Chua co tinh nang chia se |
| 8 | **Advanced Robot AI** | AI robot doi thu con don gian (collect & deliver) |
| 9 | **Offline LLM nang cao** | Ollama can may manh, chua toi uu cho ARM |
| 10 | **Opening Book / Lesson Content mo rong** | Noi dung giao duc can bo sung them |

---

## 10. SO LIEU THONG KE

| Chi so | Gia tri |
|--------|---------|
| Tong so file Python | 54 |
| Tong so dong code | ~10,228 |
| So module chinh | 9 (config, core, ai, education, hardware, storage, ui, utils, resources) |
| So UI components | 12 |
| So AI files | 7 |
| So Core files | 9 |
| So Education files | 7 |
| So bai hoc Phase 1 | 4 |
| So du an giao duc | 10 (x3 muc do = 30 phien ban) |
| So FGC field configs | 7 |

---

## 11. QUYET DINH THIET KE QUAN TRONG

### 11.1 Khong dung Tkinter cho Turtle
- Python `turtle` module phu thuoc Tkinter
- Tkinter xung dot voi PyQt6
- Giai phap: Tu xay dung TurtleCanvas bang QPainter
- Loi ich: Tich hop tot, animation dep, chay duoc tren ARM64

### 11.2 Proxy-Based Command Interception
- Hoc sinh viet code binh thuong (`import turtle`)
- He thong inject wrapper code de bat lenh
- Output la JSON qua stdout
- IDE parse va render
- Hoc sinh khong can biet ve he thong proxy

### 11.3 AI la Scaffolding, khong phai Solution Provider
- He thong NUDGE -> SOLUTION dam bao hoc sinh tu suy nghi
- Cooldown 10 giay giua cac auto-analysis
- Significance checker tranh phan hoi khong can thiet
- Muc tieu: Ho tro hoc, khong lam thay

### 11.4 Privacy-First (Khong can Server)
- Tat ca LLM calls truc tiep tu client
- Khong co backend trung tam
- Hoc sinh co the chay hoan toan offline voi rule-based hints
- Du lieu luu local (SQLite)

### 11.5 Multi-Phase Progression
- Phase 1: Turtle Graphics (truc quan, vui, de hieu)
- Phase 2: IoT/Hardware (thuc te, ung dung)
- Lo trinh ro rang tu co ban den nang cao

---

## 12. SO DO COMPONENT INTERACTION

```
                    +------------------+
                    |   MainWindow     |
                    |  (Split Layout)  |
                    +--------+---------+
                             |
          +------------------+------------------+
          |                  |                  |
   +------v------+   +------v------+   +------v------+
   |  Left Panel |   |Center Panel |   | Right Panel |
   |             |   |             |   |             |
   | CodeEditor  |   | TurtleCanvas|   | AIChatPanel |
   | EditorTool  |   |    hoac     |   | AIInput     |
   |             |   | RobotArena  |   | Progress    |
   | OutputPanel |   |             |   |             |
   +------+------+   +------+------+   +------+------+
          |                  |                  |
          +------------------+------------------+
                             |
                      +------v------+
                      |  SignalBus  |
                      +------+------+
                             |
          +------------------+------------------+
          |                  |                  |
   +------v------+   +------v------+   +------v------+
   |CodeAnalyzer |   | Execution   |   |    AI       |
   |  Worker     |   |  Engine     |   | Assistant   |
   +------+------+   +------+------+   +------+------+
          |                  |                  |
          v                  v                  v
   [AnalysisResult]  [ExecutionResult]  [AIResponse]
                     [DrawCommands]
                     [RobotCommands]
```

---

*Tai lieu nay duoc tao tu dong boi Claude Code vao ngay 2026-02-26.*
*Dua tren phan tich toan bo 54 file source code cua NEO_CODE.*
