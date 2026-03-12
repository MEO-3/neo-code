"""
output_parser — reads stdout lines from the subprocess and classifies them.

Lines that are valid JSON objects are emitted as canvas_command signals.
All other lines are emitted as stdout_received.
"""

import json

from neo_code.core.event_bus import event_bus


def parse_line(line: str) -> None:
    """
    Called for each line of subprocess stdout.
    Emits either canvas_command or stdout_received on the event_bus.
    """
    stripped = line.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            cmd = json.loads(stripped)
            if isinstance(cmd, dict) and "cmd" in cmd:
                event_bus.canvas_command.emit(cmd)
                return
        except json.JSONDecodeError:
            pass
    event_bus.stdout_received.emit(line.rstrip("\n"))
