# NEO CODE GTK - Application Context & Architecture

## 1. App Overview
**NEO CODE** is an educational Integrated Development Environment (IDE) designed for STEM and Robotics students (aged 6-12) to learn Python programming. 

The application is being rebuilt from a PyQt6 architecture to **Python GTK4 (PyGObject)** to run efficiently on low-resource Armbian devices.

### Target Hardware Constraints
* **OS:** Armbian (Linux)
* **Memory:** 2GB RAM 
* **Storage:** 16GB eMMC
* **Constraint Strategy:** To operate smoothly within these limits, the application avoids heavy web frameworks (like Electron) and uses a deferred-loading Plugin Architecture. Heavy features (like LLM-based AI and Hardware GPIO) are isolated and only loaded into memory when explicitly enabled.

---

## 2. Technology Stack
* **Language:** Python 3.11+
* **GUI Framework:** PyGObject (GTK4 + Libadwaita)
* **Code Editor Component:** GtkSourceView 5 (Native syntax highlighting, line numbers)
* **Drawing & Graphics:** Cairo (for Turtle and Robot 2D Canvases)
* **Event System:** PyPubSub (for decoupled messaging)
* **Static Analysis:** PyFlakes + Python `ast` module (Lightweight offline checks)
* **Code Completion:** Jedi (Lightweight local autocompletion)

---

## 3. Core Architecture
The system uses a highly decoupled, **Event-Driven Extension Architecture**.

### 1. Core Shell (Minimal IDE)
The core application knows nothing about educational tools, AI, or robots. It only manages:
* The Main Paned Window layout (Editor, Output Terminal, Side Panels).
* The File System (Open/Save files).
* The Event Bus (`PyPubSub`).
* The Extension Manager.

### 2. Event Bus (PubSub System)
All components communicate via events instead of direct calls. 
* *Example:* When a user clicks "Run", the Core fires an `execution_started` event. When the code outputs JSON data, it fires a `stdout_received` event, which the active Canvas plugin listens to.

### 3. Extension System (Plugins)
Every actual feature in the app is an extension. This saves RAM by preventing unused modules from being imported.
* **Built-in Extensions (Loaded by default):**
  * **Turtle Canvas:** Renders step-by-step turtle graphics.
  * **Robot Arena:** 2D physics simulation for FGC robot challenges.
  * **Curriculum Manager:** Loads the 10 built-in educational projects (Levels 1-3).
* **Future Extensions (Deferred loading):**
  * **AI Assistant:** Uses local `Ollama` or cloud APIs to provide scaffolding hints (Nudge -> Guidance -> Explicit -> Solution).
  * **Hardware/IoT:** Interfaces with GPIO pins (`gpiozero`) for Phase 2 hardware learning.

---

## 4. Execution Flow & Sandboxing
To prevent student code from freezing the GTK UI or crashing the system:
1. **Wrapper Injection:** Student code (`import turtle`) is intercepted. The IDE injects a proxy wrapper before running it.
2. **Subprocess Execution:** Code runs in an isolated Python `subprocess` with memory and timeout limits.
3. **JSON Output:** Instead of opening native windows, the proxy wrapper forces the code to output JSON commands to `stdout` (e.g., `{"cmd": "forward", "args": [100]}`).
4. **UI Thread Safe Rendering:** The background execution thread uses `GLib.idle_add()` to safely pass these JSON commands back to the GTK main thread, where Cairo draws them onto the `Gtk.DrawingArea`.

---

## 5. Development Roadmap
* **Phase 1: Core IDE Foundation** - Setup GTK4 UI, GtkSourceView, File management, and Subprocess Execution.
* **Phase 2: Visual Environments** - Implement Cairo drawing for Turtle Graphics and Robot Arena via the proxy pattern.
* **Phase 3: Curriculum & Progression** - Add SQLite local storage for student profiles, error tracking, and project templates.
* **Phase 4 (Future): Extensions** - Build the AI Chat assistant and Hardware/GPIO modules as installable plugins.