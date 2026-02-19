"""Educational phase management."""
from __future__ import annotations


from dataclasses import dataclass


@dataclass
class Phase:
    """An educational phase definition."""

    id: int
    name: str
    description: str
    required_imports: list[str]
    starter_code: str


PHASES = {
    1: Phase(
        id=1,
        name="Python & Turtle Graphics",
        description="Learn Python basics through drawing with Turtle graphics",
        required_imports=["turtle"],
        starter_code='''import turtle

# Create a turtle
t = turtle.Turtle()

# Try drawing a square!
for i in range(4):
    t.forward(100)
    t.right(90)

turtle.done()
''',
    ),
    2: Phase(
        id=2,
        name="IoT & Smart Devices",
        description="Control LEDs, sensors, and motors with Python",
        required_imports=["gpiozero"],
        starter_code='''from gpiozero import LED, Button
from time import sleep

# Connect an LED to GPIO pin 17
led = LED(17)

# Blink the LED
for i in range(5):
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)

print("Done!")
''',
    ),
}


class PhaseManager:
    """Manages educational phases and transitions."""

    def __init__(self, default_phase: int = 1):
        self._current_phase_id = default_phase

    @property
    def current_phase(self) -> Phase:
        return PHASES[self._current_phase_id]

    @property
    def current_phase_id(self) -> int:
        return self._current_phase_id

    def switch_phase(self, phase_id: int) -> Phase:
        """Switch to a different phase."""
        if phase_id not in PHASES:
            raise ValueError(f"Unknown phase: {phase_id}")
        self._current_phase_id = phase_id
        return self.current_phase

    def get_starter_code(self) -> str:
        """Get the starter code for the current phase."""
        return self.current_phase.starter_code

    def get_all_phases(self) -> list[Phase]:
        """Get all available phases."""
        return list(PHASES.values())
