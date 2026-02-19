"""Robot command interpreter that translates robot calls to RobotCommands.

Follows the same wrapper proxy pattern as turtle_interpreter.py:
Student code imports 'robot' → proxy captures calls → JSON stdout → arena widget.
"""
from __future__ import annotations

from neo_code.core.robot_models import RobotCommand, RobotCommandType
from neo_code.config.settings import get_settings


def generate_robot_wrapper_code(game_id: str = "eco_equilibrium_2025") -> str:
    """Generate Python code that wraps the robot module to capture commands.

    This code is prepended to student's robot code before execution.
    It serializes robot calls to stdout as __NEO_ROBOT__:{json} so the
    IDE can render them on the arena canvas.
    """
    max_cmds = get_settings().execution.max_robot_commands
    return f'''
import sys
import json
import time
import types

_MAX_ROBOT_COMMANDS = {max_cmds}

class _NeoRobotProxy:
    """Proxy that captures robot commands and prints them as JSON."""

    def __init__(self):
        self._x = 0.0
        self._y = 0.0
        self._heading = 0.0
        self._cmd_count = 0
        self._strategy = "balanced"

    def _emit(self, cmd_type, *args, **kwargs):
        self._cmd_count += 1
        if self._cmd_count > _MAX_ROBOT_COMMANDS:
            if self._cmd_count == _MAX_ROBOT_COMMANDS + 1:
                print(f"__NEO_ROBOT_LIMIT__:{{_MAX_ROBOT_COMMANDS}}", flush=True)
                print(f"Error: Qua nhieu lenh robot! Gioi han {{_MAX_ROBOT_COMMANDS}} lenh. "
                      f"Hay giam so lan lap lai.", file=sys.stderr, flush=True)
            sys.exit(1)
        data = {{"cmd": cmd_type, "args": list(args), "kwargs": dict(kwargs)}}
        print(f"__NEO_ROBOT__:{{json.dumps(data)}}", flush=True)
        time.sleep(0.01)

    def _emit_and_wait(self, cmd_type, *args, **kwargs):
        """Emit command and return response (for sensors/state queries)."""
        self._cmd_count += 1
        if self._cmd_count > _MAX_ROBOT_COMMANDS:
            if self._cmd_count == _MAX_ROBOT_COMMANDS + 1:
                print(f"__NEO_ROBOT_LIMIT__:{{_MAX_ROBOT_COMMANDS}}", flush=True)
            sys.exit(1)
        data = {{"cmd": cmd_type, "args": list(args), "kwargs": dict(kwargs)}}
        print(f"__NEO_ROBOT__:{{json.dumps(data)}}", flush=True)
        time.sleep(0.01)
        # Sensors return placeholder values since we cannot do IPC back
        return None

    # === Movement ===

    def forward(self, distance=100):
        """Move robot forward by distance (mm)."""
        self._emit("FORWARD", distance)

    def backward(self, distance=100):
        """Move robot backward by distance (mm)."""
        self._emit("BACKWARD", distance)

    def turn_left(self, angle=90):
        """Turn robot left by angle (degrees)."""
        self._emit("TURN_LEFT", angle)

    def turn_right(self, angle=90):
        """Turn robot right by angle (degrees)."""
        self._emit("TURN_RIGHT", angle)

    def stop(self):
        """Stop robot movement."""
        self._emit("STOP")

    # === Actions ===

    def grab(self):
        """Pick up nearest game piece within range."""
        self._emit("GRAB")

    def release(self):
        """Release held game piece (scores if in zone)."""
        self._emit("RELEASE")

    def shoot(self, power=50):
        """Launch held piece in current heading direction (power 0-100)."""
        self._emit("SHOOT", power)

    # === Sensors ===

    def distance_sensor(self):
        """Return distance to nearest obstacle (mm). Placeholder: 1000."""
        self._emit_and_wait("DISTANCE_SENSOR")
        return 1000

    def color_sensor(self):
        """Return color of nearest game piece. Placeholder: 'unknown'."""
        self._emit_and_wait("COLOR_SENSOR")
        return "unknown"

    # === State ===

    def position(self):
        """Return (x, y) position in mm."""
        self._emit_and_wait("GET_POSITION")
        return (self._x, self._y)

    def heading(self):
        """Return heading angle in degrees."""
        self._emit_and_wait("GET_HEADING")
        return self._heading

    def match_time(self):
        """Return remaining match time in seconds."""
        self._emit_and_wait("GET_MATCH_TIME")
        return 150

    def score(self):
        """Return current team score."""
        self._emit_and_wait("GET_SCORE")
        return 0

    # === Game Theory ===

    def set_strategy(self, strategy="balanced"):
        """Set robot strategy: aggressive, defensive, cooperative, balanced."""
        self._strategy = strategy
        self._emit("SET_STRATEGY", strategy)

    def get_allies(self):
        """Return list of ally robot info dicts."""
        self._emit_and_wait("GET_ALLIES")
        return []

    def get_opponents(self):
        """Return list of opponent robot info dicts."""
        self._emit_and_wait("GET_OPPONENTS")
        return []


class _RobotModule:
    """Fake robot module that provides Robot class."""

    def Robot(self):
        return _NeoRobotProxy()


# Send arena init command
_init_data = {{"cmd": "ARENA_INIT", "args": ["{game_id}"], "kwargs": {{}}}}
print(f"__NEO_ROBOT__:{{json.dumps(_init_data)}}", flush=True)
time.sleep(0.05)

# Replace robot module with proxy
_robot_module = types.ModuleType("robot")
_robot_module.Robot = _NeoRobotProxy
sys.modules["robot"] = _robot_module
'''


def parse_robot_output_line(line: str) -> RobotCommand | None:
    """Parse a robot command from the proxy's stdout output."""
    import json

    prefix = "__NEO_ROBOT__:"
    if not line.startswith(prefix):
        return None

    try:
        data = json.loads(line[len(prefix):])
        cmd_name = data.get("cmd", "")
        args = tuple(data.get("args", []))
        kwargs = data.get("kwargs", {})

        cmd_type_map = {t.name: t for t in RobotCommandType}
        cmd_type = cmd_type_map.get(cmd_name)
        if cmd_type:
            return RobotCommand(
                command_type=cmd_type,
                args=args,
                kwargs=kwargs,
            )
    except (json.JSONDecodeError, KeyError):
        pass

    return None
