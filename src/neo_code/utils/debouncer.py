"""Debouncer utility for delaying signal emission until input stops."""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class Debouncer(QObject):
    """Delays signal emission until input stops for `delay_ms` milliseconds.

    Usage:
        debouncer = Debouncer(delay_ms=500)
        editor.textChanged.connect(lambda: debouncer.call(editor.text()))
        debouncer.triggered.connect(on_code_stable)
    """

    triggered = pyqtSignal(str)

    def __init__(self, delay_ms: int = 500, parent: QObject | None = None):
        super().__init__(parent)
        self._delay = delay_ms
        self._pending_value = ""
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._emit)

    def call(self, value: str) -> None:
        """Schedule emission with the given value. Resets timer on each call."""
        self._pending_value = value
        self._timer.start(self._delay)

    def cancel(self) -> None:
        """Cancel any pending emission."""
        self._timer.stop()

    def _emit(self) -> None:
        self.triggered.emit(self._pending_value)

    @property
    def delay_ms(self) -> int:
        return self._delay

    @delay_ms.setter
    def delay_ms(self, value: int) -> None:
        self._delay = value
