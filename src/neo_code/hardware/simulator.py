"""Software simulator for hardware when no physical board is available."""
from __future__ import annotations


import logging

logger = logging.getLogger(__name__)


class HardwareSimulator:
    """Simulates GPIO/hardware for development and testing without physical board."""


    def __init__(self):
        self._pins: dict[int, dict] = {}
        self._led_states: dict[int, bool] = {}
        logger.info("Hardware simulator initialized")

    def setup_pin(self, pin: int, mode: str = "output") -> None:
        """Setup a GPIO pin."""
        self._pins[pin] = {"mode": mode, "value": 0}
        logger.info(f"[SIM] Pin {pin} set to {mode}")

    def write_pin(self, pin: int, value: int) -> None:
        """Write a value to a GPIO pin."""
        if pin in self._pins:
            self._pins[pin]["value"] = value
            self._led_states[pin] = bool(value)
            state = "ON" if value else "OFF"
            logger.info(f"[SIM] Pin {pin} = {state}")

    def read_pin(self, pin: int) -> int:
        """Read a GPIO pin value."""
        if pin in self._pins:
            return self._pins[pin]["value"]
        return 0

    def get_led_states(self) -> dict[int, bool]:
        """Get all LED states for visualization."""
        return self._led_states.copy()

    def cleanup(self) -> None:
        """Reset all pins."""
        self._pins.clear()
        self._led_states.clear()
        logger.info("[SIM] All pins cleaned up")
