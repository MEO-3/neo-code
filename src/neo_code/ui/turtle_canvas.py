"""Custom turtle graphics canvas using QPainter (no Tkinter dependency).

Features:
- KTurtle-style realistic turtle cursor (shell, head, legs, tail)
- Smooth micro-step animation system with speed control
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from PyQt6.QtCore import Qt, QPointF, QTimer, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath, QPolygonF, QTransform
from PyQt6.QtWidgets import QWidget

from neo_code.core.models import DrawCommand, DrawCommandType

# Animation constants
STEP_SIZE = 3.0        # pixels per micro-step for forward/backward
ANGLE_STEP = 5.0       # degrees per micro-step for left/right
MIN_DELAY_MS = 5       # fastest animation delay (speed 10)
MAX_DELAY_MS = 100     # slowest animation delay (speed 1)
MAX_QUEUED_COMMANDS = 100000  # safety cap for command queue


@dataclass
class MicroStep:
    """A single micro-step for smooth animation."""
    kind: Literal["move", "turn", "instant"]
    # For "move": dx, dy are deltas to move
    dx: float = 0.0
    dy: float = 0.0
    # For "turn": angle delta
    d_heading: float = 0.0
    # For "instant": full command to execute
    command: DrawCommand | None = None


class TurtleState:
    """Internal state of the turtle."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.x: float = 0.0
        self.y: float = 0.0
        self.heading: float = 90.0  # degrees, 0=east, 90=north
        self.pen_down: bool = True
        self.pen_color: str = "#cdd6f4"
        self.pen_size: int = 2
        self.fill_color: str = "#89b4fa"
        self.filling: bool = False
        self.visible: bool = True
        self.speed: int = 6


class TurtleCanvasWidget(QWidget):
    """QPainter-based turtle graphics canvas with animation and auto-fit."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._turtle = TurtleState()
        # Store in turtle coordinates (not screen coords) for auto-fit
        self._lines: list[tuple[float, float, float, float, str, int]] = []
        self._dots: list[tuple[float, float, int, str]] = []
        self._fill_paths: list[tuple[list[tuple[float, float]], str]] = []
        self._current_fill_points: list[tuple[float, float]] = []

        # Two-level animation queue
        self._command_queue: list[DrawCommand] = []  # high-level commands
        self._micro_queue: list[MicroStep] = []      # expanded micro-steps
        self._animation_timer = QTimer(self)
        self._animation_timer.setSingleShot(True)
        self._animation_timer.timeout.connect(self._tick)
        self._animating = False

        # Bounding box tracking (in turtle coords)
        self._bbox_min_x: float = 0.0
        self._bbox_max_x: float = 0.0
        self._bbox_min_y: float = 0.0
        self._bbox_max_y: float = 0.0
        self._has_content = False

        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: #11111b;")

    # === Bounding box ===

    def _update_bbox(self, x: float, y: float) -> None:
        """Expand bounding box to include point."""
        if not self._has_content:
            self._bbox_min_x = self._bbox_max_x = x
            self._bbox_min_y = self._bbox_max_y = y
            self._has_content = True
        else:
            self._bbox_min_x = min(self._bbox_min_x, x)
            self._bbox_max_x = max(self._bbox_max_x, x)
            self._bbox_min_y = min(self._bbox_min_y, y)
            self._bbox_max_y = max(self._bbox_max_y, y)

    # === Auto-fit transform ===

    def _get_transform(self) -> tuple[float, float, float]:
        """Calculate scale and offset to fit drawing in widget.

        Returns (scale, offset_x, offset_y).
        """
        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0

        if not self._has_content:
            return 1.0, cx, cy

        margin = 30
        draw_w = self._bbox_max_x - self._bbox_min_x
        draw_h = self._bbox_max_y - self._bbox_min_y

        draw_w = max(draw_w, 20) + margin * 2
        draw_h = max(draw_h, 20) + margin * 2

        avail_w = w - margin
        avail_h = h - margin

        scale_x = avail_w / draw_w if draw_w > 0 else 1.0
        scale_y = avail_h / draw_h if draw_h > 0 else 1.0
        scale = min(scale_x, scale_y, 1.5)

        draw_cx = (self._bbox_min_x + self._bbox_max_x) / 2.0
        draw_cy = (self._bbox_min_y + self._bbox_max_y) / 2.0

        off_x = cx - draw_cx * scale
        off_y = cy + draw_cy * scale  # y is flipped

        return scale, off_x, off_y

    def _to_screen(self, x: float, y: float, scale: float, off_x: float, off_y: float) -> QPointF:
        """Convert turtle coordinates to screen coordinates."""
        return QPointF(off_x + x * scale, off_y - y * scale)

    # === Painting ===

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        scale, off_x, off_y = self._get_transform()

        # Draw filled paths
        for points, color in self._fill_paths:
            if len(points) < 3:
                continue
            path = QPainterPath()
            p0 = self._to_screen(points[0][0], points[0][1], scale, off_x, off_y)
            path.moveTo(p0)
            for px, py in points[1:]:
                path.lineTo(self._to_screen(px, py, scale, off_x, off_y))
            path.closeSubpath()
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)

        # Draw lines
        for x1, y1, x2, y2, color, size in self._lines:
            start = self._to_screen(x1, y1, scale, off_x, off_y)
            end = self._to_screen(x2, y2, scale, off_x, off_y)
            pen = QPen(QColor(color), max(1, size * scale))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(start, end)

        # Draw dots
        for dx, dy, size, color in self._dots:
            center = self._to_screen(dx, dy, scale, off_x, off_y)
            r = max(1, size * scale / 2)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, r, r)

        # Draw turtle cursor (KTurtle-style)
        if self._turtle.visible:
            self._draw_turtle_cursor(painter, scale, off_x, off_y)

        painter.end()

    def _draw_turtle_cursor(self, painter: QPainter, scale: float, off_x: float, off_y: float) -> None:
        """Draw a KTurtle-style turtle: shell, head, 4 legs, tail."""
        pos = self._to_screen(self._turtle.x, self._turtle.y, scale, off_x, off_y)
        # heading: 90=north in turtle coords → screen angle needs conversion
        # In screen coords: 0=right, positive=clockwise
        # Turtle heading 90(north) → screen -90° from right → we need to rotate
        screen_angle = -self._turtle.heading  # screen rotation (clockwise positive)

        s = max(6, 10 * scale)  # base scale unit

        painter.save()
        painter.translate(pos)
        painter.rotate(90 - self._turtle.heading)  # align so 0° = heading direction pointing right

        # Colors
        shell_dark = QColor("#2d6a4f")    # dark green shell
        shell_light = QColor("#40916c")   # lighter green for pattern
        skin_color = QColor("#74c69d")    # light green skin
        eye_white = QColor("#ffffff")
        eye_black = QColor("#1b1b1b")

        # --- Tail ---
        painter.setPen(QPen(skin_color, max(1, s * 0.15)))
        painter.setBrush(QBrush(skin_color))
        tail_path = QPainterPath()
        tail_path.moveTo(-s * 1.1, 0)
        tail_path.lineTo(-s * 1.6, -s * 0.15)
        tail_path.lineTo(-s * 1.5, s * 0.05)
        tail_path.closeSubpath()
        painter.drawPath(tail_path)

        # --- Legs (4 legs) ---
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(skin_color))
        leg_positions = [
            (s * 0.4, -s * 0.6),   # front-left
            (s * 0.4, s * 0.6),    # front-right
            (-s * 0.4, -s * 0.6),  # back-left
            (-s * 0.4, s * 0.6),   # back-right
        ]
        leg_w = s * 0.3
        leg_h = s * 0.5
        for lx, ly in leg_positions:
            painter.drawEllipse(QPointF(lx, ly), leg_w, leg_h)

        # --- Shell (main oval) ---
        painter.setPen(QPen(shell_dark.darker(120), max(1, s * 0.1)))
        painter.setBrush(QBrush(shell_dark))
        painter.drawEllipse(QPointF(0, 0), s * 0.9, s * 0.7)

        # Shell pattern - hexagonal-ish lines
        painter.setPen(QPen(shell_light, max(1, s * 0.08)))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Center hex
        painter.drawEllipse(QPointF(0, 0), s * 0.3, s * 0.25)
        # Radial lines from center to edge
        for angle_deg in range(0, 360, 60):
            rad = math.radians(angle_deg)
            x1 = s * 0.3 * math.cos(rad)
            y1 = s * 0.25 * math.sin(rad)
            x2 = s * 0.85 * math.cos(rad)
            y2 = s * 0.65 * math.sin(rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # --- Head ---
        painter.setPen(QPen(skin_color.darker(110), max(1, s * 0.08)))
        painter.setBrush(QBrush(skin_color))
        head_cx = s * 1.15
        painter.drawEllipse(QPointF(head_cx, 0), s * 0.35, s * 0.3)

        # Eyes
        eye_r = s * 0.09
        eye_offset_x = s * 0.12
        eye_offset_y = s * 0.13
        for ey_sign in (-1, 1):
            # White of eye
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(eye_white))
            painter.drawEllipse(
                QPointF(head_cx + eye_offset_x, ey_sign * eye_offset_y),
                eye_r, eye_r,
            )
            # Pupil
            painter.setBrush(QBrush(eye_black))
            painter.drawEllipse(
                QPointF(head_cx + eye_offset_x + eye_r * 0.3, ey_sign * eye_offset_y),
                eye_r * 0.55, eye_r * 0.55,
            )

        painter.restore()

    # === Micro-step animation system ===

    def _speed_delay_ms(self) -> int:
        """Calculate delay per micro-step based on turtle speed setting."""
        spd = self._turtle.speed
        if spd <= 0:
            return 0  # instant
        if spd >= 10:
            return MIN_DELAY_MS
        # Linear interpolation: speed 1→MAX_DELAY_MS, speed 10→MIN_DELAY_MS
        return int(MAX_DELAY_MS - (spd - 1) * (MAX_DELAY_MS - MIN_DELAY_MS) / 9)

    def _expand_forward(self, distance: float) -> list[MicroStep]:
        """Expand forward/backward into micro-steps."""
        if abs(distance) < 0.01:
            return []
        rad = math.radians(self._turtle.heading)
        cos_h = math.cos(rad)
        sin_h = math.sin(rad)
        total = abs(distance)
        sign = 1 if distance >= 0 else -1
        steps = max(1, int(total / STEP_SIZE))
        step_dist = total / steps
        result = []
        for _ in range(steps):
            dx = sign * step_dist * cos_h
            dy = sign * step_dist * sin_h
            result.append(MicroStep(kind="move", dx=dx, dy=dy))
        return result

    def _expand_turn(self, angle: float) -> list[MicroStep]:
        """Expand left/right turn into micro-steps."""
        if abs(angle) < 0.01:
            return []
        total = abs(angle)
        sign = 1 if angle >= 0 else -1
        steps = max(1, int(total / ANGLE_STEP))
        step_angle = total / steps
        result = []
        for _ in range(steps):
            result.append(MicroStep(kind="turn", d_heading=sign * step_angle))
        return result

    def _expand_goto(self, target_x: float, target_y: float) -> list[MicroStep]:
        """Expand goto into micro-steps along a straight line."""
        t = self._turtle
        dx_total = target_x - t.x
        dy_total = target_y - t.y
        dist = math.hypot(dx_total, dy_total)
        if dist < 0.01:
            return []
        steps = max(1, int(dist / STEP_SIZE))
        dx = dx_total / steps
        dy = dy_total / steps
        return [MicroStep(kind="move", dx=dx, dy=dy) for _ in range(steps)]

    def _expand_circle(self, radius: float) -> list[MicroStep]:
        """Expand circle into move+turn micro-step pairs."""
        t = self._turtle
        steps = max(int(abs(radius) * 0.5), 36)
        angle_step = 360.0 / steps
        step_len = 2 * math.pi * abs(radius) / steps
        result = []
        # We need to simulate the heading at each step
        heading = t.heading
        for _ in range(steps):
            rad = math.radians(heading)
            dx = step_len * math.cos(rad)
            dy = step_len * math.sin(rad)
            result.append(MicroStep(kind="move", dx=dx, dy=dy))
            d_h = -angle_step if radius > 0 else angle_step
            result.append(MicroStep(kind="turn", d_heading=d_h))
            heading += d_h
        return result

    def _expand_command(self, cmd: DrawCommand) -> list[MicroStep]:
        """Expand a high-level command into micro-steps."""
        ct = cmd.command_type

        if ct == DrawCommandType.FORWARD:
            distance = cmd.args[0] if cmd.args else 0
            return self._expand_forward(distance)

        elif ct == DrawCommandType.BACKWARD:
            distance = cmd.args[0] if cmd.args else 0
            return self._expand_forward(-distance)

        elif ct == DrawCommandType.LEFT:
            angle = cmd.args[0] if cmd.args else 0
            return self._expand_turn(angle)

        elif ct == DrawCommandType.RIGHT:
            angle = cmd.args[0] if cmd.args else 0
            return self._expand_turn(-angle)

        elif ct == DrawCommandType.GOTO:
            x = float(cmd.args[0]) if len(cmd.args) > 0 else 0
            y = float(cmd.args[1]) if len(cmd.args) > 1 else 0
            return self._expand_goto(x, y)

        elif ct == DrawCommandType.CIRCLE:
            radius = cmd.args[0] if cmd.args else 50
            return self._expand_circle(radius)

        else:
            # All other commands execute instantly
            return [MicroStep(kind="instant", command=cmd)]

    # === Animation tick ===

    def process_draw_command(self, cmd: DrawCommand) -> None:
        """Queue a draw command for animated processing."""
        if len(self._command_queue) >= MAX_QUEUED_COMMANDS:
            return  # drop commands beyond safety cap
        self._command_queue.append(cmd)
        if not self._animating:
            self._animating = True
            self._tick()

    def _tick(self) -> None:
        """Main animation tick: process one micro-step or expand next command."""
        # If micro queue is empty, expand the next command
        while not self._micro_queue and self._command_queue:
            cmd = self._command_queue.pop(0)
            # Check if speed is 0 (instant) for movement commands
            if self._turtle.speed == 0 and cmd.command_type in (
                DrawCommandType.FORWARD, DrawCommandType.BACKWARD,
                DrawCommandType.LEFT, DrawCommandType.RIGHT,
                DrawCommandType.GOTO, DrawCommandType.CIRCLE,
            ):
                # Execute instantly without micro-steps
                self._execute_command_instant(cmd)
                self.update()
                continue
            micro = self._expand_command(cmd)
            self._micro_queue.extend(micro)

        if not self._micro_queue:
            self._animating = False
            self.update()
            return

        # Execute one micro-step
        step = self._micro_queue.pop(0)
        self._execute_micro(step)
        self.update()

        # Schedule next tick
        if self._micro_queue or self._command_queue:
            delay = self._speed_delay_ms()
            if delay <= 0:
                # Instant: drain all remaining micro-steps
                self._drain_all()
            else:
                # For instant-type steps (state changes), process immediately
                if step.kind == "instant":
                    self._tick()
                    return
                self._animation_timer.start(delay)
        else:
            self._animating = False

    def _drain_all(self) -> None:
        """Execute all remaining micro-steps and commands instantly."""
        while self._micro_queue:
            self._execute_micro(self._micro_queue.pop(0))
        while self._command_queue:
            cmd = self._command_queue.pop(0)
            if self._turtle.speed == 0 and cmd.command_type in (
                DrawCommandType.FORWARD, DrawCommandType.BACKWARD,
                DrawCommandType.LEFT, DrawCommandType.RIGHT,
                DrawCommandType.GOTO, DrawCommandType.CIRCLE,
            ):
                self._execute_command_instant(cmd)
            else:
                micro = self._expand_command(cmd)
                for s in micro:
                    self._execute_micro(s)
        self._animating = False
        self.update()

    def _execute_micro(self, step: MicroStep) -> None:
        """Execute a single micro-step."""
        if step.kind == "move":
            t = self._turtle
            new_x = t.x + step.dx
            new_y = t.y + step.dy
            self._move_to(new_x, new_y)
        elif step.kind == "turn":
            self._turtle.heading += step.d_heading
        elif step.kind == "instant" and step.command:
            self._execute_command_instant(step.command)

    def _execute_command_instant(self, cmd: DrawCommand) -> None:
        """Execute a full command instantly (no micro-steps)."""
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

    # === Movement ===

    def _move_to(self, new_x: float, new_y: float) -> None:
        """Move turtle to new position, drawing a line if pen is down."""
        t = self._turtle
        if t.pen_down:
            self._lines.append((t.x, t.y, new_x, new_y, t.pen_color, t.pen_size))

        if t.filling:
            self._current_fill_points.append((new_x, new_y))

        self._update_bbox(new_x, new_y)
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
        self._current_fill_points = [(self._turtle.x, self._turtle.y)]

    def _cmd_end_fill(self, args: tuple) -> None:
        self._turtle.filling = False
        if len(self._current_fill_points) > 2:
            self._fill_paths.append((list(self._current_fill_points), self._turtle.fill_color))
        self._current_fill_points = []

    def _cmd_goto(self, args: tuple) -> None:
        x = args[0] if len(args) > 0 else 0
        y = args[1] if len(args) > 1 else 0
        self._move_to(float(x), float(y))

    def _cmd_circle(self, args: tuple) -> None:
        radius = args[0] if args else 50
        t = self._turtle
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
        self._dots.append((self._turtle.x, self._turtle.y, int(size), str(color)))
        self._update_bbox(self._turtle.x, self._turtle.y)

    def _cmd_clear(self, args: tuple) -> None:
        self._lines.clear()
        self._dots.clear()
        self._fill_paths.clear()
        self._current_fill_points.clear()
        self._has_content = False
        self._bbox_min_x = self._bbox_max_x = 0.0
        self._bbox_min_y = self._bbox_max_y = 0.0

    def _cmd_reset(self, args: tuple) -> None:
        self._cmd_clear(args)
        self._turtle.reset()
        self._command_queue.clear()
        self._micro_queue.clear()
        self._animation_timer.stop()
        self._animating = False

    def _cmd_speed(self, args: tuple) -> None:
        if args:
            self._turtle.speed = int(args[0])

    def _cmd_hideturtle(self, args: tuple) -> None:
        self._turtle.visible = False

    def _cmd_showturtle(self, args: tuple) -> None:
        self._turtle.visible = True

    # === Public API ===

    def clear_canvas(self) -> None:
        """Clear all drawings."""
        self._cmd_clear(())
        self.update()

    def reset_turtle(self) -> None:
        """Reset turtle to initial state and clear drawings."""
        self._cmd_reset(())
        self.update()

    def process_commands(self, commands: list[DrawCommand]) -> None:
        """Process a batch of draw commands (queued for animation)."""
        for cmd in commands:
            self.process_draw_command(cmd)
