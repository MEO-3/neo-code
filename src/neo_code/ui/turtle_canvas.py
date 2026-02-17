"""Custom turtle graphics canvas using QPainter (no Tkinter dependency)."""

import math

from PyQt6.QtCore import Qt, QPointF, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath, QPolygonF
from PyQt6.QtWidgets import QWidget

from neo_code.core.models import DrawCommand, DrawCommandType


class TurtleState:
    """Internal state of the turtle."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.x: float = 0.0
        self.y: float = 0.0
        self.heading: float = 90.0  # degrees, 0=east, 90=north (turtle convention)
        self.pen_down: bool = True
        self.pen_color: str = "#cdd6f4"
        self.pen_size: int = 2
        self.fill_color: str = "#89b4fa"
        self.filling: bool = False
        self.visible: bool = True
        self.speed: int = 6


class TurtleCanvasWidget(QWidget):
    """QPainter-based turtle graphics canvas."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._turtle = TurtleState()
        self._lines: list[tuple[QPointF, QPointF, str, int]] = []  # (start, end, color, size)
        self._dots: list[tuple[QPointF, int, str]] = []  # (center, size, color)
        self._fill_paths: list[tuple[QPainterPath, str]] = []
        self._current_fill_points: list[QPointF] = []
        self._command_queue: list[DrawCommand] = []
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._process_next_command)

        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: #11111b;")

    def _to_screen(self, x: float, y: float) -> QPointF:
        """Convert turtle coordinates (center origin, y-up) to screen coordinates."""
        cx = self.width() / 2
        cy = self.height() / 2
        return QPointF(cx + x, cy - y)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw filled paths
        for path, color in self._fill_paths:
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)

        # Draw lines
        for start, end, color, size in self._lines:
            pen = QPen(QColor(color), size)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(start, end)

        # Draw dots
        for center, size, color in self._dots:
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, size / 2, size / 2)

        # Draw turtle cursor
        if self._turtle.visible:
            self._draw_turtle_cursor(painter)

        painter.end()

    def _draw_turtle_cursor(self, painter: QPainter) -> None:
        """Draw a triangle representing the turtle."""
        pos = self._to_screen(self._turtle.x, self._turtle.y)
        heading_rad = math.radians(self._turtle.heading)
        size = 12

        # Triangle points (pointing in heading direction)
        tip = QPointF(
            pos.x() + size * math.cos(heading_rad),
            pos.y() - size * math.sin(heading_rad),
        )
        left = QPointF(
            pos.x() + size * 0.6 * math.cos(heading_rad + 2.5),
            pos.y() - size * 0.6 * math.sin(heading_rad + 2.5),
        )
        right = QPointF(
            pos.x() + size * 0.6 * math.cos(heading_rad - 2.5),
            pos.y() - size * 0.6 * math.sin(heading_rad - 2.5),
        )

        triangle = QPolygonF([tip, left, right])
        painter.setBrush(QBrush(QColor("#a6e3a1")))
        painter.setPen(QPen(QColor("#a6e3a1"), 1))
        painter.drawPolygon(triangle)

    def process_draw_command(self, cmd: DrawCommand) -> None:
        """Process a single turtle drawing command."""
        t = self._turtle
        handlers = {
            DrawCommandType.FORWARD: self._cmd_forward,
            DrawCommandType.BACKWARD: self._cmd_backward,
            DrawCommandType.LEFT: self._cmd_left,
            DrawCommandType.RIGHT: self._cmd_right,
            DrawCommandType.PENUP: self._cmd_penup,
            DrawCommandType.PENDOWN: self._cmd_pendown,
            DrawCommandType.PENCOLOR: self._cmd_pencolor,
            DrawCommandType.PENSIZE: self._cmd_pensize,
            DrawCommandType.FILLCOLOR: self._cmd_fillcolor,
            DrawCommandType.BEGIN_FILL: self._cmd_begin_fill,
            DrawCommandType.END_FILL: self._cmd_end_fill,
            DrawCommandType.GOTO: self._cmd_goto,
            DrawCommandType.CIRCLE: self._cmd_circle,
            DrawCommandType.DOT: self._cmd_dot,
            DrawCommandType.CLEAR: self._cmd_clear,
            DrawCommandType.RESET: self._cmd_reset,
            DrawCommandType.SPEED: self._cmd_speed,
            DrawCommandType.HIDETURTLE: self._cmd_hideturtle,
            DrawCommandType.SHOWTURTLE: self._cmd_showturtle,
        }

        handler = handlers.get(cmd.command_type)
        if handler:
            handler(cmd.args)
            self.update()

    def _move_to(self, new_x: float, new_y: float) -> None:
        """Move turtle to new position, drawing a line if pen is down."""
        t = self._turtle
        if t.pen_down:
            start = self._to_screen(t.x, t.y)
            end = self._to_screen(new_x, new_y)
            self._lines.append((start, end, t.pen_color, t.pen_size))

        if t.filling:
            self._current_fill_points.append(self._to_screen(new_x, new_y))

        t.x = new_x
        t.y = new_y

    def _cmd_forward(self, args: tuple) -> None:
        distance = args[0] if args else 0
        rad = math.radians(self._turtle.heading)
        new_x = self._turtle.x + distance * math.cos(rad)
        new_y = self._turtle.y + distance * math.sin(rad)
        self._move_to(new_x, new_y)

    def _cmd_backward(self, args: tuple) -> None:
        distance = args[0] if args else 0
        rad = math.radians(self._turtle.heading)
        new_x = self._turtle.x - distance * math.cos(rad)
        new_y = self._turtle.y - distance * math.sin(rad)
        self._move_to(new_x, new_y)

    def _cmd_left(self, args: tuple) -> None:
        angle = args[0] if args else 0
        self._turtle.heading += angle

    def _cmd_right(self, args: tuple) -> None:
        angle = args[0] if args else 0
        self._turtle.heading -= angle

    def _cmd_penup(self, args: tuple) -> None:
        self._turtle.pen_down = False

    def _cmd_pendown(self, args: tuple) -> None:
        self._turtle.pen_down = True

    def _cmd_pencolor(self, args: tuple) -> None:
        if args:
            self._turtle.pen_color = str(args[0])

    def _cmd_pensize(self, args: tuple) -> None:
        if args:
            self._turtle.pen_size = int(args[0])

    def _cmd_fillcolor(self, args: tuple) -> None:
        if args:
            self._turtle.fill_color = str(args[0])

    def _cmd_begin_fill(self, args: tuple) -> None:
        self._turtle.filling = True
        self._current_fill_points = [self._to_screen(self._turtle.x, self._turtle.y)]

    def _cmd_end_fill(self, args: tuple) -> None:
        self._turtle.filling = False
        if len(self._current_fill_points) > 2:
            path = QPainterPath()
            path.moveTo(self._current_fill_points[0])
            for pt in self._current_fill_points[1:]:
                path.lineTo(pt)
            path.closeSubpath()
            self._fill_paths.append((path, self._turtle.fill_color))
        self._current_fill_points = []

    def _cmd_goto(self, args: tuple) -> None:
        x = args[0] if len(args) > 0 else 0
        y = args[1] if len(args) > 1 else 0
        self._move_to(float(x), float(y))

    def _cmd_circle(self, args: tuple) -> None:
        radius = args[0] if args else 50
        t = self._turtle
        # Approximate circle with small line segments
        steps = max(int(abs(radius) * 0.5), 36)
        angle_step = 360.0 / steps
        for _ in range(steps):
            rad = math.radians(t.heading)
            step_len = 2 * math.pi * abs(radius) / steps
            new_x = t.x + step_len * math.cos(rad)
            new_y = t.y + step_len * math.sin(rad)
            self._move_to(new_x, new_y)
            if radius > 0:
                t.heading -= angle_step
            else:
                t.heading += angle_step

    def _cmd_dot(self, args: tuple) -> None:
        size = args[0] if args else 5
        color = args[1] if len(args) > 1 else self._turtle.pen_color
        pos = self._to_screen(self._turtle.x, self._turtle.y)
        self._dots.append((pos, int(size), str(color)))

    def _cmd_clear(self, args: tuple) -> None:
        self._lines.clear()
        self._dots.clear()
        self._fill_paths.clear()
        self._current_fill_points.clear()

    def _cmd_reset(self, args: tuple) -> None:
        self._cmd_clear(args)
        self._turtle.reset()

    def _cmd_speed(self, args: tuple) -> None:
        if args:
            self._turtle.speed = int(args[0])

    def _cmd_hideturtle(self, args: tuple) -> None:
        self._turtle.visible = False

    def _cmd_showturtle(self, args: tuple) -> None:
        self._turtle.visible = True

    # Public convenience methods

    def clear_canvas(self) -> None:
        """Clear all drawings."""
        self._cmd_clear(())
        self.update()

    def reset_turtle(self) -> None:
        """Reset turtle to initial state and clear drawings."""
        self._cmd_reset(())
        self.update()

    def process_commands(self, commands: list[DrawCommand]) -> None:
        """Process a batch of draw commands."""
        for cmd in commands:
            self.process_draw_command(cmd)
