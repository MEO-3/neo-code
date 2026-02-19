"""Sensor management for reading various sensors (Phase 2)."""
from __future__ import annotations


import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SensorManager:
    """Manages sensor readings from connected hardware."""


    def __init__(self):
        self._sensors: dict[str, dict] = {}

    def register_sensor(self, name: str, sensor_type: str, pin: int) -> None:
        """Register a sensor."""
        self._sensors[name] = {
            "type": sensor_type,
            "pin": pin,
            "last_value": None,
        }
        logger.info(f"Sensor registered: {name} ({sensor_type}) on pin {pin}")

    def read(self, name: str) -> Optional[float]:
        """Read a sensor value."""
        if name not in self._sensors:
            logger.warning(f"Unknown sensor: {name}")
            return None

        # In simulation mode, return mock data
        sensor = self._sensors[name]
        mock_values = {
            "temperature": 25.0,
            "humidity": 60.0,
            "distance": 30.0,
            "light": 500.0,
        }
        value = mock_values.get(sensor["type"], 0.0)
        sensor["last_value"] = value
        return value

    def get_all_readings(self) -> dict[str, Optional[float]]:
        """Get readings from all registered sensors."""
        return {name: self.read(name) for name in self._sensors}
