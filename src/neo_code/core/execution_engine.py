"""Code execution engine with subprocess sandboxing."""

import subprocess
import sys
import time

from PyQt6.QtCore import QThread, pyqtSignal

from neo_code.config.settings import get_settings
from neo_code.core.models import ExecutionResult


class ExecutionWorker(QThread):
    """Executes student code in a sandboxed subprocess."""

    stdout_received = pyqtSignal(str)
    stderr_received = pyqtSignal(str)
    execution_started = pyqtSignal()
    execution_finished = pyqtSignal(object)  # ExecutionResult

    def __init__(self, parent=None):
        super().__init__(parent)
        self._code: str = ""
        self._process: subprocess.Popen | None = None
        self._settings = get_settings()

    def execute(self, code: str) -> None:
        """Start executing the given code."""
        self._code = code
        if not self.isRunning():
            self.start()

    def stop(self) -> None:
        """Kill the running process."""
        if self._process and self._process.poll() is None:
            self._process.kill()

    def is_executing(self) -> bool:
        """Check if code is currently running."""
        return self._process is not None and self._process.poll() is None

    def run(self) -> None:
        self.execution_started.emit()
        start_time = time.time()

        try:
            self._process = subprocess.Popen(
                [sys.executable, "-u", "-c", self._code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            stdout_data = ""
            stderr_data = ""

            # Read stdout in real-time
            if self._process.stdout:
                for line in self._process.stdout:
                    stdout_data += line
                    self.stdout_received.emit(line)

            # Wait for process to finish
            self._process.wait(timeout=self._settings.execution.timeout_seconds)

            # Read any remaining stderr
            if self._process.stderr:
                stderr_data = self._process.stderr.read()
                if stderr_data:
                    self.stderr_received.emit(stderr_data)

            elapsed_ms = (time.time() - start_time) * 1000

            result = ExecutionResult(
                stdout=stdout_data,
                stderr=stderr_data,
                return_code=self._process.returncode,
                execution_time_ms=elapsed_ms,
            )

        except subprocess.TimeoutExpired:
            self._process.kill()
            elapsed_ms = (time.time() - start_time) * 1000
            self.stderr_received.emit("Execution timed out!\n")
            result = ExecutionResult(
                stdout="", stderr="Timeout", return_code=-1,
                execution_time_ms=elapsed_ms, was_timeout=True,
            )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.stderr_received.emit(f"Execution error: {e}\n")
            result = ExecutionResult(
                stdout="", stderr=str(e), return_code=-1,
                execution_time_ms=elapsed_ms,
            )

        finally:
            self._process = None
            self.execution_finished.emit(result)
