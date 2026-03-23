# 📖 Lesson Feature — Architecture and UX Design

## Overview

The **Lesson Feature** is a guided learning system inside NEO Code designed to help children (Grade 3–10) learn Python through **interactive, hands-on coding activities**.

Instead of traditional tutorials, lessons are structured as **short, game-like challenges** that emphasize:

* Immediate feedback
* Small wins
* Learning by doing

---

## 🎯 Goals

* Teach fundamental Python concepts (print, variables, logic, loops)
* Build confidence through quick success cycles
* Provide a clear progression path from beginner → intermediate
* Keep kids engaged through interactivity and gamification

---

## 🧠 Core Learning Principle

> Learn by doing:
> **Try → See → Fix → Win**

Each lesson should:

* Be short (5–10 minutes)
* Have a clear goal
* Provide instant feedback
* Encourage experimentation

---

## 🗂️ Lesson Structure

Lessons are organized as:

```
World → Lesson → Challenge
```

Example:

```
World 1 — First Code
  Lesson 1 — Say Hello
  Lesson 2 — Your Name
  Lesson 3 — Multiple Lines

World 2 — Variables
  Lesson 4 — Store a Value
  Lesson 5 — Numbers
```

---

## 🏗️ Architecture (Minimal Core Changes)

**Goal:** Implement Lesson as a self-contained feature that interacts with the IDE through existing EventBus signals and widgets, without modifying core execution or adding new global events.

### ✅ Key Principle
Use the existing **EventBus** and **editor/runner** APIs as integration points.
No new signals are required; the feature manages its own lifecycle internally.

---

### 1. Feature-Local Lifecycle
A simple state machine inside `LessonFeature` coordinates lesson flow:

```
Idle → Loaded → Active → Running → Active → Idle
```

**Lifecycle methods (feature-only):**
- `load_lesson(lesson_id)`
- `enter_lesson()` — inject starter code, prepare UI
- `run()` — emit `execution_requested(code)`
- `on_stdout(text)`
- `on_stderr(text)`
- `on_finished(exit_code)` — evaluate + show feedback
- `exit_lesson()` — restore IDE state

---

### 2. Existing EventBus Signals Used
The lesson feature listens to existing signals only:

- `execution_requested(code)` → run lesson code
- `stdout_received(text)` → capture output
- `stderr_received(text)` → capture errors
- `execution_finished(exit_code)` → finalize evaluation
- `code_changed(code)` → track edits (optional)

**No new core signals added.**

---

### 3. Internal Components (Feature Scope Only)

```
features/lessons/
  feature.py            # LessonFeature(IFeature)
  lesson_lifecycle.py   # Local state machine
  lesson_sidebar.py     # World/Lesson list
  lesson_workspace.py   # Goal/Hint/Editor/Output/Feedback
  models.py             # World, Lesson, Challenge
  loader.py             # Load JSON/YAML lesson packs
  evaluator.py          # Validate output / AST / rules
  feedback_mapper.py    # Kid-friendly messages
  progress_store.py     # SQLite / JSON for progress
```

---

### 4. Execution Flow (No Core Changes)

```
[Run in Lesson UI]
     │
     ├─ emit execution_requested(code)
     │
     └─ LessonFeature listens to:
            stdout_received / stderr_received / execution_finished
                ↓
         LessonEvaluator → FeedbackMapper → UI Feedback
```

---

### 5. Lesson UI Integration Strategy
- Lesson runs **inside its own panel**, not modifying the main editor layout.
- Uses a local editor widget or the existing editor panel in a controlled mode.
- Output shown in lesson panel (can mirror terminal output).

---

### ✅ Result
This architecture keeps the **core IDE stable** and puts all lesson behavior inside the feature, while still allowing full interaction with execution, output, and progress tracking.

---

## 🧩 Lesson Format

Each lesson follows a consistent structure:

### 1. 🎯 Goal

Clear, simple objective

> "Make the computer say Hello"

### 2. 💡 Hint

Short explanation (1–2 lines max)

> "Use print() to show text"

### 3. 🧪 Coding Area

Interactive editor where kids write code

### 4. ▶ Run Button

Execute code instantly

### 5. 📺 Output Panel

Shows result of the code

### 6. ✅ Feedback

* Success → celebration
* Failure → helpful hint (not raw errors)

---

## 🧠 Curriculum (First 10 Lessons)

### World 1 — First Code

1. Say Hello → `print()`
2. Your Name → strings
3. Multiple Lines → sequence

---

### World 2 — Variables

4. Store a Value → variables
5. Numbers → basic math

---

### World 3 — Decisions

6. If Statement → conditions
7. If Else → branching

---

### World 4 — Loops

8. Repeat → `for` loop
9. Counting → loop variables

---

### World 5 — Mini Logic

10. Mini Game → combine concepts

---

## 🎮 Activity Types

To keep engagement high, lessons should include:

### 1. Fill in the blank

```python
print(____)
```

### 2. Fix the bug

```python
pritn("Hello")
```

### 3. Predict output

Show code → ask result

### 4. Free play

Open-ended exploration

---

## ⚡ Feedback System

### ❌ Avoid

Raw Python errors:

```
NameError: x is not defined
```

### ✅ Use

Kid-friendly feedback:

```
❌ Oops! You used a variable that doesn’t exist yet.
Try creating it first!
```

---

## 🏆 Progress System

Optional but highly recommended:

* ⭐ Stars per lesson (1–3)
* 📈 Progress bar
* 🏅 Badges (e.g. "Loop Master")

Example:

```
[★★☆] Lesson Complete!
```

---

## 🎨 UX Design

### Layout

```
┌──────────────────────────────┐
│ 🎯 Goal                      │
├──────────────┬───────────────┤
│ 💡 Hint      │ 🧪 Editor     │
│              │               │
├──────────────┴───────────────┤
│ ▶ Run                        │
├──────────────────────────────┤
│ 📺 Output                    │
├──────────────────────────────┤
│ ✅ Feedback                  │
└──────────────────────────────┘
```

---

## 🧒 Age Adaptation

| Age   | Focus                  |
| ----- | ---------------------- |
| 8–10  | print, sequence        |
| 10–12 | variables, loops       |
| 12–16 | logic, problem solving |

---

## ⚠️ Design Principles

### DO

* Keep instructions short
* Give instant feedback
* Celebrate success
* Encourage experimentation

### DON’T

* Show long explanations
* Use technical jargon
* Block creativity too early
* Show raw Python errors

---

## 🚀 Future Extensions

* Interactive quizzes
* Story-based missions
* Integration with Robot Feature
* Adaptive difficulty
* Save/load progress

---

## Summary

The Lesson Feature transforms NEO Code from an IDE into a **learning platform**.

It focuses on:

* simplicity
* interactivity
* progression
* fun

The goal is not just to teach Python —
but to make kids feel:

> “I can code.”

