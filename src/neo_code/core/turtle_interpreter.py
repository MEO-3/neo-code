"""Turtle command interpreter that translates turtle calls to DrawCommands."""
from __future__ import annotations


import re

from neo_code.core.models import DrawCommand, DrawCommandType
from neo_code.config.settings import get_settings


# Map turtle method names to DrawCommandType
TURTLE_COMMAND_MAP = {
    "forward": DrawCommandType.FORWARD,
    "fd": DrawCommandType.FORWARD,
    "backward": DrawCommandType.BACKWARD,
    "bk": DrawCommandType.BACKWARD,
    "back": DrawCommandType.BACKWARD,
    "left": DrawCommandType.LEFT,
    "lt": DrawCommandType.LEFT,
    "right": DrawCommandType.RIGHT,
    "rt": DrawCommandType.RIGHT,
    "penup": DrawCommandType.PENUP,
    "pu": DrawCommandType.PENUP,
    "up": DrawCommandType.PENUP,
    "pendown": DrawCommandType.PENDOWN,
    "pd": DrawCommandType.PENDOWN,
    "down": DrawCommandType.PENDOWN,
    "pencolor": DrawCommandType.PENCOLOR,
    "color": DrawCommandType.PENCOLOR,
    "pensize": DrawCommandType.PENSIZE,
    "width": DrawCommandType.PENSIZE,
    "fillcolor": DrawCommandType.FILLCOLOR,
    "begin_fill": DrawCommandType.BEGIN_FILL,
    "end_fill": DrawCommandType.END_FILL,
    "goto": DrawCommandType.GOTO,
    "setpos": DrawCommandType.GOTO,
    "setposition": DrawCommandType.GOTO,
    "circle": DrawCommandType.CIRCLE,
    "dot": DrawCommandType.DOT,
    "clear": DrawCommandType.CLEAR,
    "reset": DrawCommandType.RESET,
    "speed": DrawCommandType.SPEED,
    "stamp": DrawCommandType.STAMP,
    "hideturtle": DrawCommandType.HIDETURTLE,
    "ht": DrawCommandType.HIDETURTLE,
    "showturtle": DrawCommandType.SHOWTURTLE,
    "st": DrawCommandType.SHOWTURTLE,
}

# Regex to match turtle method calls
# e.g., t.forward(100), turtle.left(90), forward(50)
TURTLE_CALL_RE = re.compile(
    r'(?:\w+\.)?(' + '|'.join(re.escape(k) for k in TURTLE_COMMAND_MAP) + r')\s*\(([^)]*)\)'
)


def parse_turtle_commands(code: str) -> list[DrawCommand]:
    """Parse turtle commands from Python code into DrawCommands.


    This is a static analysis approach - it extracts turtle calls from the code
    text. For runtime interception, use the execution engine's turtle redirect.
    """
    commands = []

    for match in TURTLE_CALL_RE.finditer(code):
        method_name = match.group(1)
        args_str = match.group(2).strip()

        cmd_type = TURTLE_COMMAND_MAP.get(method_name)
        if cmd_type is None:
            continue

        # Parse arguments
        args = _parse_args(args_str)
        commands.append(DrawCommand(command_type=cmd_type, args=tuple(args)))

    return commands


def _parse_args(args_str: str) -> list:
    """Parse a comma-separated argument string into a list of values."""
    if not args_str:
        return []

    args = []
    for part in args_str.split(","):
        part = part.strip().strip("'\"")
        if not part:
            continue
        try:
            # Try as number first
            if "." in part:
                args.append(float(part))
            else:
                args.append(int(part))
        except ValueError:
            # Keep as string
            args.append(part)

    return args


def generate_turtle_wrapper_code() -> str:
    """Generate Python code that wraps the turtle module to capture commands.

    This code is prepended to student's turtle code before execution.
    It serializes turtle calls to stdout in a parseable format so the
    IDE can render them on the custom canvas.
    """
    max_cmds = get_settings().execution.max_turtle_commands
    return f'''
import sys
import json

_MAX_TURTLE_COMMANDS = {max_cmds}

class _NeoTurtleProxy:
    """Proxy that captures turtle commands and prints them as JSON."""

    def __init__(self):
        self._x = 0.0
        self._y = 0.0
        self._heading = 90.0
        self._pen_down = True
        self._cmd_count = 0

    def _emit(self, cmd_type, *args):
        self._cmd_count += 1
        if self._cmd_count > _MAX_TURTLE_COMMANDS:
            if self._cmd_count == _MAX_TURTLE_COMMANDS + 1:
                print(f"__NEO_TURTLE_LIMIT__:{{_MAX_TURTLE_COMMANDS}}", flush=True)
                print(f"Error: Qua nhieu lenh turtle! Gioi han {{_MAX_TURTLE_COMMANDS}} lenh. "
                      f"Hay giam so lan lap lai.", file=sys.stderr, flush=True)
            sys.exit(1)
        data = {{"cmd": cmd_type, "args": list(args)}}
        print(f"__NEO_TURTLE__:{{json.dumps(data)}}", flush=True)

    def forward(self, distance):
        self._emit("FORWARD", distance)
    fd = forward

    def backward(self, distance):
        self._emit("BACKWARD", distance)
    bk = back = backward

    def left(self, angle):
        self._emit("LEFT", angle)
    lt = left

    def right(self, angle):
        self._emit("RIGHT", angle)
    rt = right

    def penup(self):
        self._emit("PENUP")
    pu = up = penup

    def pendown(self):
        self._emit("PENDOWN")
    pd = down = pendown

    def pencolor(self, *args):
        self._emit("PENCOLOR", *args)
    color = pencolor

    def pensize(self, width):
        self._emit("PENSIZE", width)
    width = pensize

    def fillcolor(self, *args):
        self._emit("FILLCOLOR", *args)

    def begin_fill(self):
        self._emit("BEGIN_FILL")

    def end_fill(self):
        self._emit("END_FILL")

    def goto(self, x, y=None):
        if y is None and hasattr(x, '__iter__'):
            x, y = x
        self._emit("GOTO", x, y or 0)
    setpos = setposition = goto

    def circle(self, radius, extent=None, steps=None):
        self._emit("CIRCLE", radius)

    def dot(self, size=None, color=None):
        self._emit("DOT", size or 5, color or "")

    def clear(self):
        self._emit("CLEAR")

    def reset(self):
        self._emit("RESET")

    def speed(self, speed):
        self._emit("SPEED", speed)

    def hideturtle(self):
        self._emit("HIDETURTLE")
    ht = hideturtle

    def showturtle(self):
        self._emit("SHOWTURTLE")
    st = showturtle

    def done(self):
        pass

    def mainloop(self):
        pass

    def exitonclick(self):
        pass

    def Turtle(self):
        return self

    def Screen(self):
        return self

    def setup(self, *args, **kwargs):
        pass

    def title(self, *args):
        pass

    def bgcolor(self, *args):
        pass

# Replace turtle module with proxy
import types
_proxy = _NeoTurtleProxy()
turtle = types.ModuleType("turtle")
turtle.Turtle = lambda: _proxy
turtle.Screen = lambda: _proxy
turtle.forward = _proxy.forward
turtle.fd = _proxy.fd
turtle.backward = _proxy.backward
turtle.bk = _proxy.bk
turtle.back = _proxy.back
turtle.left = _proxy.left
turtle.lt = _proxy.lt
turtle.right = _proxy.right
turtle.rt = _proxy.rt
turtle.penup = _proxy.penup
turtle.pu = _proxy.pu
turtle.pendown = _proxy.pendown
turtle.pd = _proxy.pd
turtle.pencolor = _proxy.pencolor
turtle.color = _proxy.color
turtle.pensize = _proxy.pensize
turtle.fillcolor = _proxy.fillcolor
turtle.begin_fill = _proxy.begin_fill
turtle.end_fill = _proxy.end_fill
turtle.goto = _proxy.goto
turtle.circle = _proxy.circle
turtle.dot = _proxy.dot
turtle.clear = _proxy.clear
turtle.reset = _proxy.reset
turtle.speed = _proxy.speed
turtle.hideturtle = _proxy.hideturtle
turtle.ht = _proxy.ht
turtle.showturtle = _proxy.showturtle
turtle.st = _proxy.st
turtle.done = _proxy.done
turtle.mainloop = _proxy.mainloop
turtle.exitonclick = _proxy.exitonclick
turtle.setup = _proxy.setup
turtle.title = _proxy.title
turtle.bgcolor = _proxy.bgcolor
sys.modules["turtle"] = turtle
'''


def parse_turtle_output_line(line: str) -> DrawCommand | None:
    """Parse a turtle command from the proxy's stdout output."""
    import json

    prefix = "__NEO_TURTLE__:"
    if not line.startswith(prefix):
        return None

    try:
        data = json.loads(line[len(prefix):])
        cmd_name = data.get("cmd", "")
        args = tuple(data.get("args", []))

        cmd_type_map = {t.name: t for t in DrawCommandType}
        cmd_type = cmd_type_map.get(cmd_name)
        if cmd_type:
            return DrawCommand(command_type=cmd_type, args=args)
    except (json.JSONDecodeError, KeyError):
        pass

    return None
