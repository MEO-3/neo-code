"""Robot Arena canvas widget - QPainter-based 2D field renderer.

Follows the same pattern as TurtleCanvasWidget:
command queue → tick timer → physics engine → QPainter render.
"""
from __future__ import annotations

import math
from collections import deque

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPolygonF,
    QPainterPath, QLinearGradient,
)
from PyQt6.QtWidgets import QWidget

from neo_code.core.robot_models import (
    RobotCommand, RobotCommandType, FieldConfig, ArenaState,
    PieceType, Alliance, ObstacleShape, RobotState, GamePiece,
    FieldMission,
)
from neo_code.core.robot_physics import ArenaPhysicsEngine

MAX_QUEUED_COMMANDS = 50000
COMMANDS_PER_TICK = 3
MARGIN = 40


class RobotArenaWidget(QWidget):
    """2D robot arena canvas with physics simulation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self._engine: ArenaPhysicsEngine | None = None
        self._command_queue: deque[RobotCommand] = deque(maxlen=MAX_QUEUED_COMMANDS)
        self._field_config: FieldConfig | None = None

        # Animation timer (30 FPS)
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(33)  # ~30 FPS
        self._tick_timer.timeout.connect(self._tick)

        # Feedback popups: list of {text, x, y, color, ttl}
        self._feedback_popups: list[dict] = []

        # Colors
        self._bg_color = QColor("#1a1a2e")
        self._field_color = QColor("#2d2d44")
        self._grid_color = QColor(255, 255, 255, 30)
        self._text_color = QColor("#cdd6f4")

        self.setStyleSheet("background-color: #1a1a2e;")

    def process_robot_command(self, cmd: RobotCommand) -> None:
        """Queue a robot command for processing."""
        if cmd.command_type == RobotCommandType.ARENA_INIT:
            game_id = cmd.args[0] if cmd.args else "eco_equilibrium_2025"
            self.set_field(game_id)
            return
        self._command_queue.append(cmd)
        if not self._tick_timer.isActive():
            self._tick_timer.start()

    def set_field(self, field_id: str) -> None:
        """Load and initialize a field config."""
        from neo_code.education.robot_challenges import get_field_config
        config = get_field_config(field_id)
        if config:
            self._field_config = config
            self._engine = ArenaPhysicsEngine(config)
            self._engine.initialize_robots()
            self._command_queue.clear()
            self._tick_timer.start()
            self.update()

    def reset_arena(self) -> None:
        """Reset arena to initial state."""
        self._tick_timer.stop()
        self._command_queue.clear()
        self._engine = None
        self._field_config = None
        self._feedback_popups.clear()
        self.update()

    def _tick(self) -> None:
        """Process commands and advance physics each frame."""
        if not self._engine:
            return

        # Process N commands per tick
        for _ in range(COMMANDS_PER_TICK):
            if not self._command_queue:
                break
            cmd = self._command_queue.popleft()
            self._engine.process_command(cmd)

        # Process feedback events from physics engine
        self._process_feedback_events()

        # Advance physics (AI robots, timer)
        self._engine.tick(1.0 / 30.0)

        # Tick down popup TTLs
        for popup in self._feedback_popups:
            popup["ttl"] -= 1
            popup["y"] -= 1.5  # float upward
        self._feedback_popups = [p for p in self._feedback_popups if p["ttl"] > 0]

        # Stop timer if no more commands and match ended
        if not self._command_queue and not self._engine.state.match_running:
            self._tick_timer.stop()

        self.update()

    # === Coordinate transform ===

    def _get_transform(self) -> tuple[float, float, float]:
        """Calculate scale and offset to fit field in widget.
        Returns (scale, offset_x, offset_y).
        """
        if not self._field_config:
            return 1.0, 0.0, 0.0
        fw = self._field_config.field_width
        fh = self._field_config.field_height
        ww = self.width() - 2 * MARGIN
        wh = self.height() - 2 * MARGIN
        scale = min(ww / fw, wh / fh)
        ox = MARGIN + (ww - fw * scale) / 2
        oy = MARGIN + (wh - fh * scale) / 2
        return scale, ox, oy

    def _to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Convert field mm coords to screen pixels (Y flipped)."""
        scale, ox, oy = self._get_transform()
        fh = self._field_config.field_height if self._field_config else 7000
        sx = ox + x * scale
        sy = oy + (fh - y) * scale  # Y flipped
        return sx, sy

    # === Painting ===

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), self._bg_color)

        if not self._field_config or not self._engine:
            self._draw_placeholder(painter)
            painter.end()
            return

        state = self._engine.state
        scale, ox, oy = self._get_transform()

        # Field background
        self._draw_field(painter, scale, ox, oy)
        # Grid
        self._draw_grid(painter, scale, ox, oy)
        # Coordinate marks on field edges
        self._draw_coordinate_marks(painter, scale, ox, oy)
        # Scoring zones
        self._draw_scoring_zones(painter, state, scale)
        # Obstacles
        self._draw_obstacles(painter, scale)
        # Game pieces
        self._draw_game_pieces(painter, state, scale)
        # Piece labels
        self._draw_piece_labels(painter, state, scale)
        # Grab range indicator
        self._draw_grab_range(painter, state, scale)
        # Path preview
        self._draw_path_preview(painter, state, scale)
        # Robot trails
        self._draw_trails(painter, state, scale)
        # Robots
        self._draw_robots(painter, state, scale)
        # Mission objectives panel
        self._draw_mission_objectives(painter, state)
        # HUD overlay
        self._draw_hud(painter, state)
        # Feedback popups (on top of everything)
        self._draw_feedback_popups(painter)

        painter.end()

    def _draw_placeholder(self, painter: QPainter) -> None:
        painter.setPen(QPen(self._text_color))
        font = QFont("JetBrains Mono", 14)
        painter.setFont(font)
        painter.drawText(
            self.rect(), Qt.AlignmentFlag.AlignCenter,
            "Robot Arena\nChon bai Robot tu Samples de bat dau"
        )

    def _draw_field(self, painter: QPainter, scale: float,
                    ox: float, oy: float) -> None:
        fc = self._field_config
        if not fc:
            return
        w = fc.field_width * scale
        h = fc.field_height * scale
        # Field gradient
        grad = QLinearGradient(ox, oy, ox, oy + h)
        grad.setColorAt(0, QColor("#2a2a40"))
        grad.setColorAt(1, QColor("#1e1e30"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#45475a"), 2))
        painter.drawRect(QRectF(ox, oy, w, h))

    def _draw_grid(self, painter: QPainter, scale: float,
                   ox: float, oy: float) -> None:
        fc = self._field_config
        if not fc:
            return
        painter.setPen(QPen(self._grid_color, 1))
        step = 1000  # 1m grid
        # Vertical lines
        x = 0.0
        while x <= fc.field_width:
            sx = ox + x * scale
            painter.drawLine(
                QPointF(sx, oy),
                QPointF(sx, oy + fc.field_height * scale),
            )
            x += step
        # Horizontal lines
        y = 0.0
        while y <= fc.field_height:
            sy = oy + (fc.field_height - y) * scale
            painter.drawLine(
                QPointF(ox, sy),
                QPointF(ox + fc.field_width * scale, sy),
            )
            y += step

    def _draw_scoring_zones(self, painter: QPainter, state: ArenaState,
                            scale: float) -> None:
        fc = self._field_config
        if not fc:
            return
        for zone in fc.scoring_zones:
            color = QColor(zone.color)
            color.setAlpha(60)
            sx, sy = self._to_screen(zone.x, zone.y + zone.height)
            w = zone.width * scale
            h = zone.height * scale
            painter.setBrush(QBrush(color))
            border_color = QColor(zone.color)
            border_color.setAlpha(150)
            painter.setPen(QPen(border_color, 2, Qt.PenStyle.DashLine))
            painter.drawRect(QRectF(sx, sy, w, h))
            # Label
            if zone.label:
                painter.setPen(QPen(QColor(zone.color), 1))
                font = QFont("JetBrains Mono", max(8, int(12 * scale / 0.1)))
                font.setPixelSize(max(10, int(14 * scale * 10)))
                painter.setFont(QFont("JetBrains Mono", 9))
                painter.drawText(
                    QRectF(sx, sy, w, h),
                    Qt.AlignmentFlag.AlignCenter,
                    zone.label,
                )

    def _draw_obstacles(self, painter: QPainter, scale: float) -> None:
        fc = self._field_config
        if not fc:
            return
        for obs in fc.obstacles:
            color = QColor(obs.color)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(130), 1))
            sx, sy = self._to_screen(obs.x, obs.y + obs.height)
            w = obs.width * scale
            h = obs.height * scale
            if obs.shape == ObstacleShape.CIRCLE:
                r = max(w, h) / 2
                painter.drawEllipse(QPointF(sx + w / 2, sy + h / 2), r, r)
            else:
                painter.drawRect(QRectF(sx, sy, w, h))

    def _draw_game_pieces(self, painter: QPainter, state: ArenaState,
                          scale: float) -> None:
        for piece in state.game_pieces:
            if piece.collected_by is not None:
                continue  # held by robot, drawn with robot
            color = QColor(piece.color)
            sx, sy = self._to_screen(piece.x, piece.y)
            size = max(8, 15 * scale * 5)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.lighter(150), 1))
            if piece.type == PieceType.BALL:
                painter.drawEllipse(QPointF(sx, sy), size, size)
            elif piece.type == PieceType.CUBE:
                painter.drawRect(QRectF(sx - size, sy - size, size * 2, size * 2))
            else:  # CYLINDER
                painter.drawRoundedRect(
                    QRectF(sx - size, sy - size * 0.7, size * 2, size * 1.4),
                    3, 3,
                )

    def _draw_trails(self, painter: QPainter, state: ArenaState,
                     scale: float) -> None:
        for robot in state.robots.values():
            if len(robot.trail) < 2:
                continue
            color = QColor("#ef4444") if robot.alliance == Alliance.RED else QColor("#3b82f6")
            color.setAlpha(40 if not robot.is_player else 80)
            painter.setPen(QPen(color, max(1, 2 * scale * 5)))
            for i in range(1, len(robot.trail)):
                x1, y1 = self._to_screen(*robot.trail[i - 1])
                x2, y2 = self._to_screen(*robot.trail[i])
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _draw_robots(self, painter: QPainter, state: ArenaState,
                     scale: float) -> None:
        for robot in state.robots.values():
            sx, sy = self._to_screen(robot.x, robot.y)
            r = max(10, 250 * scale)  # robot radius in pixels

            # Robot body
            if robot.alliance == Alliance.RED:
                body_color = QColor("#ef4444")
                dark_color = QColor("#b91c1c")
            else:
                body_color = QColor("#3b82f6")
                dark_color = QColor("#1d4ed8")

            # Shadow
            painter.setBrush(QBrush(QColor(0, 0, 0, 40)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(sx + 2, sy + 2), r, r)

            # Body circle
            painter.setBrush(QBrush(body_color))
            painter.setPen(QPen(dark_color, 2))
            painter.drawEllipse(QPointF(sx, sy), r, r)

            # Direction arrow
            rad = math.radians(robot.heading)
            # In screen coords, Y is flipped
            ax = sx + r * 0.8 * math.cos(rad)
            ay = sy - r * 0.8 * math.sin(rad)  # minus for screen Y flip
            painter.setPen(QPen(QColor("#ffffff"), max(1, r * 0.15)))
            painter.drawLine(QPointF(sx, sy), QPointF(ax, ay))
            # Arrow head
            arrow_size = r * 0.3
            a1 = rad + math.radians(150)
            a2 = rad - math.radians(150)
            p1 = QPointF(ax + arrow_size * math.cos(a1), ay - arrow_size * math.sin(a1))
            p2 = QPointF(ax + arrow_size * math.cos(a2), ay - arrow_size * math.sin(a2))
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(QPolygonF([QPointF(ax, ay), p1, p2]))

            # Player star indicator
            if robot.is_player:
                painter.setPen(QPen(QColor("#fbbf24"), 2))
                painter.setBrush(QBrush(QColor("#fbbf24")))
                star_r = r * 0.3
                self._draw_star(painter, sx, sy - r - star_r - 2, star_r)

            # Holding indicator
            if robot.holding:
                painter.setBrush(QBrush(QColor("#fbbf24")))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(sx, sy), r * 0.25, r * 0.25)

            # Robot ID label
            painter.setPen(QPen(QColor("#ffffff")))
            font = QFont("JetBrains Mono", max(7, int(r * 0.4)))
            painter.setFont(font)
            label = "P" if robot.is_player else robot.id[:3]
            painter.drawText(
                QRectF(sx - r, sy - r * 0.3, r * 2, r * 0.6),
                Qt.AlignmentFlag.AlignCenter, label,
            )

    def _draw_star(self, painter: QPainter, cx: float, cy: float, r: float) -> None:
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            radius = r if i % 2 == 0 else r * 0.4
            points.append(QPointF(cx + radius * math.cos(angle),
                                  cy + radius * math.sin(angle)))
        painter.drawPolygon(QPolygonF(points))

    def _draw_coordinate_marks(self, painter: QPainter, scale: float,
                               ox: float, oy: float) -> None:
        """Draw coordinate numbers (0, 1000, 2000...) along field edges."""
        fc = self._field_config
        if not fc:
            return
        font = QFont("JetBrains Mono", 8)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255, 100)))
        step = 1000
        # Bottom edge (X axis)
        x = 0.0
        while x <= fc.field_width:
            sx = ox + x * scale
            sy = oy + fc.field_height * scale + 14
            painter.drawText(QPointF(sx - 10, sy), str(int(x)))
            x += step
        # Left edge (Y axis)
        y = 0.0
        while y <= fc.field_height:
            sx = ox - 30
            sy = oy + (fc.field_height - y) * scale + 4
            painter.drawText(QPointF(sx, sy), str(int(y)))
            y += step

    def _draw_piece_labels(self, painter: QPainter, state: ArenaState,
                           scale: float) -> None:
        """Draw text labels below each visible game piece."""
        font = QFont("JetBrains Mono", max(7, int(10 * scale * 8)))
        painter.setFont(font)
        for piece in state.game_pieces:
            if piece.collected_by is not None or not piece.label:
                continue
            sx, sy = self._to_screen(piece.x, piece.y)
            size = max(8, 15 * scale * 5)
            painter.setPen(QPen(QColor(255, 255, 255, 200)))
            painter.drawText(
                QRectF(sx - 40, sy + size + 2, 80, 16),
                Qt.AlignmentFlag.AlignCenter, piece.label,
            )

    def _draw_grab_range(self, painter: QPainter, state: ArenaState,
                         scale: float) -> None:
        """Draw dashed circle around player robot showing grab range (300mm)."""
        player = state.robots.get("player")
        if not player:
            return
        sx, sy = self._to_screen(player.x, player.y)
        grab_r = 300 * scale  # PICKUP_RANGE_MM in pixels
        pen = QPen(QColor("#fbbf24"), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(sx, sy), grab_r, grab_r)
        # Label
        font = QFont("JetBrains Mono", 7)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#fbbf24", ), 1))
        painter.drawText(
            QRectF(sx - 40, sy + grab_r + 2, 80, 14),
            Qt.AlignmentFlag.AlignCenter, "Vung nhat",
        )

    def _draw_path_preview(self, painter: QPainter, state: ArenaState,
                           scale: float) -> None:
        """Draw a dotted green line showing forward direction from player robot."""
        player = state.robots.get("player")
        if not player:
            return
        sx, sy = self._to_screen(player.x, player.y)
        preview_len = 1000 * scale  # 1m preview
        rad = math.radians(player.heading)
        ex = sx + preview_len * math.cos(rad)
        ey = sy - preview_len * math.sin(rad)  # Y flipped
        pen = QPen(QColor("#22c55e"), 1, Qt.PenStyle.DotLine)
        painter.setPen(pen)
        painter.drawLine(QPointF(sx, sy), QPointF(ex, ey))
        # Arrow head at end
        arrow_size = 6
        a1 = rad + math.radians(150)
        a2 = rad - math.radians(150)
        p1 = QPointF(ex + arrow_size * math.cos(a1), ey - arrow_size * math.sin(a1))
        p2 = QPointF(ex + arrow_size * math.cos(a2), ey - arrow_size * math.sin(a2))
        painter.setBrush(QBrush(QColor("#22c55e")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF([QPointF(ex, ey), p1, p2]))

    def _draw_mission_objectives(self, painter: QPainter, state: ArenaState) -> None:
        """Draw mission objectives panel in bottom-left corner."""
        mission = state.active_mission
        if not mission:
            return
        panel_w = 260
        line_h = 18
        header_h = 22
        panel_h = header_h + len(mission.objectives) * line_h + 8
        px = 8
        py = self.height() - panel_h - 58  # above status bar

        # Semi-transparent background
        painter.setBrush(QBrush(QColor(0, 0, 0, 160)))
        painter.setPen(QPen(QColor("#45475a"), 1))
        painter.drawRoundedRect(QRectF(px, py, panel_w, panel_h), 6, 6)

        # Header
        font = QFont("JetBrains Mono", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#cdd6f4")))
        painter.drawText(
            QRectF(px + 8, py + 4, panel_w - 16, header_h),
            Qt.AlignmentFlag.AlignVCenter,
            f"Nhiem vu: {mission.name}",
        )

        # Objectives
        font = QFont("JetBrains Mono", 8)
        painter.setFont(font)
        for i, obj in enumerate(mission.objectives):
            oy = py + header_h + i * line_h
            if obj.completed or obj.id in state.completed_objectives:
                check = "[V]"
                color = QColor("#22c55e")
            else:
                check = "[ ]"
                color = QColor("#9ca3af")
            painter.setPen(QPen(color))
            painter.drawText(
                QRectF(px + 8, oy, panel_w - 16, line_h),
                Qt.AlignmentFlag.AlignVCenter,
                f"{check} {obj.order}. {obj.description}",
            )

    def _draw_feedback_popups(self, painter: QPainter) -> None:
        """Draw floating text popups that fade out."""
        for popup in self._feedback_popups:
            alpha = min(255, popup["ttl"] * 6)
            color = QColor(popup.get("color", "#ffffff"))
            color.setAlpha(alpha)
            font_size = popup.get("font_size", 12)
            font = QFont("JetBrains Mono", font_size, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(color))
            # Shadow
            shadow = QColor(0, 0, 0, alpha // 2)
            painter.setPen(QPen(shadow))
            painter.drawText(QPointF(popup["x"] + 1, popup["y"] + 1), popup["text"])
            # Text
            painter.setPen(QPen(color))
            painter.drawText(QPointF(popup["x"], popup["y"]), popup["text"])

    def _process_feedback_events(self) -> None:
        """Convert physics feedback_queue events into visual popups."""
        if not self._engine:
            return
        queue = self._engine.state.feedback_queue
        while queue:
            event = queue.pop(0)
            fx = event.get("x", 0)
            fy = event.get("y", 0)
            sx, sy = self._to_screen(fx, fy)
            etype = event.get("type", "")
            message = event.get("message", "")
            if etype == "score":
                color = "#22c55e"
                font_size = 14
                ttl = 60
            elif etype == "grab_success":
                color = "#fbbf24"
                font_size = 11
                ttl = 45
            elif etype == "objective_complete":
                color = "#38bdf8"
                font_size = 12
                ttl = 60
            elif etype == "action_fail":
                color = "#f87171"
                font_size = 10
                ttl = 40
            else:
                color = "#ffffff"
                font_size = 10
                ttl = 30
            self._feedback_popups.append({
                "text": message,
                "x": sx - 30,
                "y": sy - 20,
                "color": color,
                "font_size": font_size,
                "ttl": ttl,
            })

    def _draw_hud(self, painter: QPainter, state: ArenaState) -> None:
        """Draw heads-up display: timer, scores, game name."""
        # Semi-transparent top bar
        bar_h = 50
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(0, 0, self.width(), bar_h))

        # Game name (left)
        painter.setPen(QPen(self._text_color))
        font = QFont("JetBrains Mono", 11, QFont.Weight.Bold)
        painter.setFont(font)
        name = state.field_config.name if state.field_config else "Robot Arena"
        painter.drawText(QRectF(10, 0, 300, bar_h),
                         Qt.AlignmentFlag.AlignVCenter, name)

        # Timer (center)
        time_remaining = max(0, state.time_remaining)
        minutes = int(time_remaining) // 60
        seconds = int(time_remaining) % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"
        timer_color = QColor("#f59e0b") if time_remaining < 30 else self._text_color
        painter.setPen(QPen(timer_color))
        font = QFont("JetBrains Mono", 18, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            QRectF(0, 0, self.width(), bar_h),
            Qt.AlignmentFlag.AlignCenter, timer_text,
        )

        # Scores (right)
        red_score = state.scores.get("red", 0)
        blue_score = state.scores.get("blue", 0)
        font = QFont("JetBrains Mono", 13, QFont.Weight.Bold)
        painter.setFont(font)

        # Red score
        painter.setPen(QPen(QColor("#ef4444")))
        painter.drawText(
            QRectF(self.width() - 220, 0, 100, bar_h),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
            f"RED {red_score}",
        )

        # Separator
        painter.setPen(QPen(self._text_color))
        painter.drawText(
            QRectF(self.width() - 120, 0, 20, bar_h),
            Qt.AlignmentFlag.AlignCenter, "-",
        )

        # Blue score
        painter.setPen(QPen(QColor("#3b82f6")))
        painter.drawText(
            QRectF(self.width() - 100, 0, 90, bar_h),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            f"{blue_score} BLUE",
        )

        # Match status
        if not state.match_running and state.time_remaining <= 0:
            painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(
                self.width() / 2 - 100, self.height() / 2 - 25, 200, 50,
            ))
            painter.setPen(QPen(QColor("#fbbf24")))
            font = QFont("JetBrains Mono", 16, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(
                QRectF(self.width() / 2 - 100, self.height() / 2 - 25, 200, 50),
                Qt.AlignmentFlag.AlignCenter, "MATCH OVER",
            )
