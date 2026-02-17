"""GPIO abstraction layer for hardware interaction (Phase 2)."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GPIOWrapper:
    """Abstraction over GPIO libraries for hardware interaction."""

    def __init__(self):
        self._available = False
        self._library = None
        self._detect_hardware()

    def _detect_hardware(self) -> None:
        """Detect available GPIO library."""
        try:
            import gpiozero
            self._library = "gpiozero"
            self._available = True
            logger.info("GPIO available via gpiozero")
        except ImportError:
            try:
                import RPi.GPIO
                self._library = "RPi.GPIO"
                self._available = True
                logger.info("GPIO available via RPi.GPIO")
            except ImportError:
                logger.info("No GPIO library available - hardware features disabled")

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def library_name(self) -> Optional[str]:
        return self._library

    def get_status(self) -> dict:
        """Get hardware status info."""
        return {
            "available": self._available,
            "library": self._library or "none",
        }
