"""
runner — executes student code in an isolated QProcess.

Uses QProcess so stdout/stderr callbacks arrive on the Qt event loop —
no manual threading or GLib.idle_add() needed.

Listens to:
  event_bus.execution_requested  (code: str)
  event_bus.execution_stop_requested

Emits:
  event_bus.execution_started
  event_bus.execution_finished   (exit_code: int)
  event_bus.stdout_received      (text: str)      — via output_parser
  event_bus.stderr_received      (text: str)
  event_bus.canvas_command       (cmd: dict)       — via output_parser
"""

import sys
import os
from pathlib import Path

from PyQt5.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSlot

from neo_code.core.event_bus import event_bus
from neo_code.execution.proxy_injector import prepare_script
from neo_code.execution import output_parser

# Execution limits
_TIMEOUT_MS = 30_000   # 30 seconds hard kill


class Runner(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._process: QProcess | None = None
        self._tmp_script: Path | None = None

        event_bus.execution_requested.connect(self._on_execution_requested)
        event_bus.execution_stop_requested.connect(self._on_stop_requested)

    # ── Slots ─────────────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_execution_requested(self, code: str) -> None:
        if self._process and self._process.state() != QProcess.NotRunning:
            return  # already running

        self._tmp_script = prepare_script(code)

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.SeparateChannels)
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        env.insert("PYTHONUTF8", "1")
        self._process.setProcessEnvironment(env)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        event_bus.execution_started.emit()
        self._process.start(sys.executable, ["-X", "utf8", str(self._tmp_script)])

        # Safety timeout
        from PyQt5.QtCore import QTimer
        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.setInterval(_TIMEOUT_MS)
        self._timeout_timer.timeout.connect(self._on_timeout)
        self._timeout_timer.start()

    @pyqtSlot()
    def _on_stop_requested(self) -> None:
        self._kill_process()

    # ── Process callbacks ─────────────────────────────────────────────────────

    @pyqtSlot()
    def _on_stdout(self) -> None:
        if self._process is None:
            return
        while self._process.canReadLine():
            line = bytes(self._process.readLine()).decode("utf-8", errors="replace")
            output_parser.parse_line(line)

    @pyqtSlot()
    def _on_stderr(self) -> None:
        if self._process is None:
            return
        data = bytes(self._process.readAllStandardError()).decode("utf-8", errors="replace")
        for line in data.splitlines():
            event_bus.stderr_received.emit(line)

    @pyqtSlot(int, QProcess.ExitStatus)
    def _on_finished(self, exit_code: int, _status) -> None:
        self._cleanup()
        event_bus.execution_finished.emit(exit_code)

    def _on_timeout(self) -> None:
        event_bus.stderr_received.emit("⏱  Execution timed out (30s limit).")
        self._kill_process()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _kill_process(self) -> None:
        if self._process and self._process.state() != QProcess.NotRunning:
            self._process.kill()
            self._process.waitForFinished(1000)

    def _cleanup(self) -> None:
        if hasattr(self, "_timeout_timer"):
            self._timeout_timer.stop()
        if self._tmp_script and self._tmp_script.exists():
            try:
                os.unlink(self._tmp_script)
            except OSError:
                pass
        self._tmp_script = None
        self._process = None
