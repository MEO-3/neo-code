"""
EventBus — singleton QObject with typed Qt signals.

All inter-component communication goes through this object.
No component should call another component directly to trigger behaviour.

Usage:
    from neo_code.core.event_bus import event_bus

    # Connect
    event_bus.file_opened.connect(my_slot)

    # Emit
    event_bus.file_opened.emit(path, content)
"""

from PyQt5.QtCore import QObject, pyqtSignal


class EventBus(QObject):

    # ── File lifecycle ─────────────────────────────────────────────────────
    file_new = pyqtSignal()                     # new blank file requested
    file_opened = pyqtSignal(str, str)          # (path, content)
    file_saved = pyqtSignal(str)                # (path,)

    # ── Code / Editor ──────────────────────────────────────────────────────
    code_changed = pyqtSignal(str)              # (code,)  debounced

    # ── Execution ──────────────────────────────────────────────────────────
    execution_requested = pyqtSignal(str)       # (code,)
    execution_stop_requested = pyqtSignal()
    execution_started = pyqtSignal()
    execution_finished = pyqtSignal(int)        # (exit_code,)

    # ── Subprocess output ──────────────────────────────────────────────────
    stdout_received = pyqtSignal(str)           # (text,)
    stderr_received = pyqtSignal(str)           # (text,)
    canvas_command = pyqtSignal(dict)           # (cmd dict)  e.g. {"cmd":"forward","args":[100]}

    # ── Curriculum ─────────────────────────────────────────────────────────
    project_opened = pyqtSignal(object)         # (Project,)

    # ── UI dialogs (toolbar → main_window) ────────────────────────────────
    open_file_dialog_requested = pyqtSignal()
    save_file_dialog_requested = pyqtSignal()


# Module-level singleton — import this everywhere
event_bus = EventBus()
