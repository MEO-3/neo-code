"""2D physics engine for Robot Arena simulation."""
from __future__ import annotations

import math
import random
from typing import Optional

from neo_code.core.robot_models import (
    RobotCommand, RobotCommandType, RobotState, GamePiece,
    FieldConfig, ArenaState, Alliance, ScoringZone,
    MissionObjectiveType,
)


# Physics constants (mm)
ROBOT_RADIUS = 250
PICKUP_RANGE_MM = 300
SHOOT_DISTANCE = 2000
ROBOT_SPEED = 500       # mm per command (forward/backward distance unit)
AI_SPEED = 200          # mm per tick for AI robots


class ArenaPhysicsEngine:
    """Handles all physics simulation for the robot arena."""

    def __init__(self, field_config: FieldConfig):
        self.state = ArenaState(field_config=field_config)
        self.state.time_remaining = field_config.match_duration
        self.state.game_pieces = [
            GamePiece(
                id=p.id, type=p.type, x=p.x, y=p.y,
                color=p.color, value=p.value, label=p.label,
            )
            for p in field_config.game_pieces
        ]
        self._ai_targets: dict[str, Optional[str]] = {}
        # Init active mission from field config
        if field_config.missions:
            self.state.active_mission = field_config.missions[0]

    def initialize_robots(self) -> None:
        """Place robots at their starting positions."""
        fc = self.state.field_config
        if not fc:
            return
        for robot_id, (x, y, heading) in fc.robot_start_positions.items():
            alliance = Alliance.RED if "red" in robot_id else Alliance.BLUE
            is_player = robot_id == "player"
            self.state.robots[robot_id] = RobotState(
                id=robot_id, x=x, y=y, heading=heading,
                alliance=alliance, is_player=is_player,
            )
        self.state.match_running = True
        self.state.scores = {"red": 0, "blue": 0}

    def process_command(self, cmd: RobotCommand) -> dict:
        """Process a single robot command, return response dict."""
        robot = self.state.robots.get(cmd.robot_id)
        if not robot:
            # Default to player robot
            robot = self.state.robots.get("player")
        if not robot:
            return {"error": "no robot"}

        ct = cmd.command_type
        handlers = {
            RobotCommandType.FORWARD: self._cmd_forward,
            RobotCommandType.BACKWARD: self._cmd_backward,
            RobotCommandType.TURN_LEFT: self._cmd_turn_left,
            RobotCommandType.TURN_RIGHT: self._cmd_turn_right,
            RobotCommandType.STOP: self._cmd_stop,
            RobotCommandType.GRAB: self._cmd_grab,
            RobotCommandType.RELEASE: self._cmd_release,
            RobotCommandType.SHOOT: self._cmd_shoot,
            RobotCommandType.DISTANCE_SENSOR: self._cmd_distance_sensor,
            RobotCommandType.COLOR_SENSOR: self._cmd_color_sensor,
            RobotCommandType.GET_POSITION: self._cmd_get_position,
            RobotCommandType.GET_HEADING: self._cmd_get_heading,
            RobotCommandType.GET_MATCH_TIME: self._cmd_get_match_time,
            RobotCommandType.GET_SCORE: self._cmd_get_score,
            RobotCommandType.GET_ALLIES: self._cmd_get_allies,
            RobotCommandType.GET_OPPONENTS: self._cmd_get_opponents,
            RobotCommandType.SET_STRATEGY: self._cmd_set_strategy,
        }
        handler = handlers.get(ct)
        if handler:
            return handler(robot, cmd.args, cmd.kwargs)
        return {}

    def tick(self, dt: float) -> None:
        """Advance simulation by dt seconds."""
        if not self.state.match_running:
            return
        self.state.time_remaining -= dt
        if self.state.time_remaining <= 0:
            self.state.time_remaining = 0
            self.state.match_running = False
            return
        self._tick_ai_robots(dt)

    # === Command handlers ===

    def _cmd_forward(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        distance = args[0] if args else 100
        rad = math.radians(robot.heading)
        new_x = robot.x + distance * math.cos(rad)
        new_y = robot.y + distance * math.sin(rad)
        new_x, new_y = self._clamp_position(new_x, new_y)
        if not self._check_obstacle_collision(robot.x, robot.y, new_x, new_y):
            robot.trail.append((robot.x, robot.y))
            robot.x = new_x
            robot.y = new_y
            self._update_held_piece(robot)
        self._check_objectives(robot)
        return {"x": robot.x, "y": robot.y}

    def _cmd_backward(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        distance = args[0] if args else 100
        rad = math.radians(robot.heading)
        new_x = robot.x - distance * math.cos(rad)
        new_y = robot.y - distance * math.sin(rad)
        new_x, new_y = self._clamp_position(new_x, new_y)
        if not self._check_obstacle_collision(robot.x, robot.y, new_x, new_y):
            robot.trail.append((robot.x, robot.y))
            robot.x = new_x
            robot.y = new_y
            self._update_held_piece(robot)
        self._check_objectives(robot)
        return {"x": robot.x, "y": robot.y}

    def _cmd_turn_left(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        angle = args[0] if args else 90
        robot.heading = (robot.heading + angle) % 360
        return {"heading": robot.heading}

    def _cmd_turn_right(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        angle = args[0] if args else 90
        robot.heading = (robot.heading - angle) % 360
        return {"heading": robot.heading}

    def _cmd_stop(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        return {"stopped": True}

    def _cmd_grab(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        if robot.holding:
            self._queue_feedback({
                "type": "action_fail", "message": "Dang giu vat roi!",
                "x": robot.x, "y": robot.y,
            })
            return {"grabbed": False, "reason": "already holding"}
        nearest = self._find_nearest_piece(robot.x, robot.y, PICKUP_RANGE_MM)
        if nearest:
            nearest.collected_by = robot.id
            robot.holding = nearest.id
            label = nearest.label or nearest.id
            self._queue_feedback({
                "type": "grab_success", "message": f"Nhat {label}!",
                "x": robot.x, "y": robot.y,
            })
            self._check_objectives(robot)
            return {"grabbed": True, "piece_id": nearest.id}
        self._queue_feedback({
            "type": "action_fail", "message": "Khong co vat nao gan!",
            "x": robot.x, "y": robot.y,
        })
        return {"grabbed": False, "reason": "no piece in range"}

    def _cmd_release(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        if not robot.holding:
            self._queue_feedback({
                "type": "action_fail", "message": "Khong giu vat nao!",
                "x": robot.x, "y": robot.y,
            })
            return {"released": False, "reason": "not holding"}
        piece = self._get_piece_by_id(robot.holding)
        if piece:
            piece.collected_by = None
            piece.x = robot.x
            piece.y = robot.y
            # Check scoring
            zone = self._check_scoring_zone(piece.x, piece.y)
            if zone:
                piece.in_zone = zone.id
                alliance_key = robot.alliance.value
                points = piece.value * zone.multiplier
                self.state.scores[alliance_key] = self.state.scores.get(alliance_key, 0) + points
                robot.score += points
                robot.holding = None
                self._queue_feedback({
                    "type": "score", "message": f"+{points}!",
                    "x": robot.x, "y": robot.y, "points": points,
                })
                self._check_objectives(robot)
                return {"released": True, "scored": True, "points": points, "zone": zone.label}
            self._queue_feedback({
                "type": "action_fail", "message": "Ngoai zone - khong ghi diem!",
                "x": robot.x, "y": robot.y,
            })
        robot.holding = None
        self._check_objectives(robot)
        return {"released": True, "scored": False}

    def _cmd_shoot(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        if not robot.holding:
            self._queue_feedback({
                "type": "action_fail", "message": "Khong giu vat nao!",
                "x": robot.x, "y": robot.y,
            })
            return {"shot": False, "reason": "not holding"}
        power = args[0] if args else 50
        power = max(0, min(100, power))
        piece = self._get_piece_by_id(robot.holding)
        if piece:
            distance = SHOOT_DISTANCE * (power / 100.0)
            rad = math.radians(robot.heading)
            piece.x = robot.x + distance * math.cos(rad)
            piece.y = robot.y + distance * math.sin(rad)
            piece.x, piece.y = self._clamp_position(piece.x, piece.y)
            piece.collected_by = None
            # Check if it landed in a scoring zone
            zone = self._check_scoring_zone(piece.x, piece.y)
            if zone:
                piece.in_zone = zone.id
                alliance_key = robot.alliance.value
                points = piece.value * zone.multiplier
                self.state.scores[alliance_key] = self.state.scores.get(alliance_key, 0) + points
                robot.score += points
                robot.holding = None
                self._queue_feedback({
                    "type": "score", "message": f"+{points}!",
                    "x": piece.x, "y": piece.y, "points": points,
                })
                self._check_objectives(robot)
                return {"shot": True, "scored": True, "points": points}
            self._queue_feedback({
                "type": "action_fail", "message": "Ban truot!",
                "x": piece.x, "y": piece.y,
            })
        robot.holding = None
        self._check_objectives(robot)
        return {"shot": True, "scored": False}

    def _cmd_distance_sensor(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        dist = self._raycast_distance(robot)
        return {"distance": dist}

    def _cmd_color_sensor(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        nearest = self._find_nearest_piece(robot.x, robot.y, PICKUP_RANGE_MM * 2)
        color = nearest.color if nearest else "none"
        return {"color": color}

    def _cmd_get_position(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        return {"x": robot.x, "y": robot.y}

    def _cmd_get_heading(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        return {"heading": robot.heading}

    def _cmd_get_match_time(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        return {"time": self.state.time_remaining}

    def _cmd_get_score(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        alliance_key = robot.alliance.value
        return {"score": self.state.scores.get(alliance_key, 0)}

    def _cmd_get_allies(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        allies = []
        for r in self.state.robots.values():
            if r.id != robot.id and r.alliance == robot.alliance:
                allies.append({"id": r.id, "x": r.x, "y": r.y, "heading": r.heading})
        return {"allies": allies}

    def _cmd_get_opponents(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        opponents = []
        for r in self.state.robots.values():
            if r.alliance != robot.alliance:
                opponents.append({"id": r.id, "x": r.x, "y": r.y, "heading": r.heading})
        return {"opponents": opponents}

    def _cmd_set_strategy(self, robot: RobotState, args: tuple, kwargs: dict) -> dict:
        strategy = args[0] if args else "balanced"
        return {"strategy": strategy}

    # === Feedback & Objectives ===

    def _queue_feedback(self, event: dict) -> None:
        """Push visual feedback event for arena widget to render."""
        self.state.feedback_queue.append(event)

    def _check_objectives(self, robot: RobotState) -> None:
        """Check if any mission objectives are completed after a command."""
        if not robot.is_player:
            return
        mission = self.state.active_mission
        if not mission:
            return
        for obj in mission.objectives:
            if obj.completed or obj.id in self.state.completed_objectives:
                continue
            if self._evaluate_objective(obj, robot):
                obj.completed = True
                self.state.completed_objectives.append(obj.id)
                self._queue_feedback({
                    "type": "objective_complete",
                    "message": f"V {obj.description}",
                    "x": robot.x, "y": robot.y,
                })

    def _evaluate_objective(self, obj, robot: RobotState) -> bool:
        """Evaluate whether a single objective is met."""
        otype = obj.objective_type
        if otype == MissionObjectiveType.MOVE_TO:
            dist = math.hypot(robot.x - obj.target_x, robot.y - obj.target_y)
            return dist <= obj.target_radius
        elif otype == MissionObjectiveType.GRAB_PIECE:
            if obj.target_piece_id:
                return robot.holding == obj.target_piece_id
            return robot.holding is not None
        elif otype == MissionObjectiveType.RELEASE_IN_ZONE:
            if obj.target_zone_id:
                for piece in self.state.game_pieces:
                    if piece.in_zone == obj.target_zone_id and piece.collected_by is None:
                        return True
            return False
        elif otype == MissionObjectiveType.SCORE_POINTS:
            alliance_key = robot.alliance.value
            return self.state.scores.get(alliance_key, 0) >= obj.target_score
        elif otype == MissionObjectiveType.COLLECT_N:
            count = sum(
                1 for p in self.state.game_pieces
                if p.collected_by == robot.id or p.in_zone is not None
            )
            return count >= obj.target_count
        return False

    # === Physics helpers ===

    def _clamp_position(self, x: float, y: float) -> tuple[float, float]:
        fc = self.state.field_config
        if not fc:
            return x, y
        margin = ROBOT_RADIUS
        x = max(margin, min(fc.field_width - margin, x))
        y = max(margin, min(fc.field_height - margin, y))
        return x, y

    def _check_obstacle_collision(self, old_x: float, old_y: float,
                                   new_x: float, new_y: float) -> bool:
        fc = self.state.field_config
        if not fc:
            return False
        for obs in fc.obstacles:
            # Simple AABB collision
            if (obs.x - ROBOT_RADIUS < new_x < obs.x + obs.width + ROBOT_RADIUS and
                    obs.y - ROBOT_RADIUS < new_y < obs.y + obs.height + ROBOT_RADIUS):
                return True
        return False

    def _find_nearest_piece(self, x: float, y: float,
                            max_range: float) -> Optional[GamePiece]:
        nearest = None
        nearest_dist = max_range
        for piece in self.state.game_pieces:
            if piece.collected_by is not None:
                continue
            dist = math.hypot(piece.x - x, piece.y - y)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = piece
        return nearest

    def _get_piece_by_id(self, piece_id: str) -> Optional[GamePiece]:
        for piece in self.state.game_pieces:
            if piece.id == piece_id:
                return piece
        return None

    def _check_scoring_zone(self, x: float, y: float) -> Optional[ScoringZone]:
        fc = self.state.field_config
        if not fc:
            return None
        for zone in fc.scoring_zones:
            if (zone.x <= x <= zone.x + zone.width and
                    zone.y <= y <= zone.y + zone.height):
                return zone
        return None

    def _update_held_piece(self, robot: RobotState) -> None:
        if robot.holding:
            piece = self._get_piece_by_id(robot.holding)
            if piece:
                piece.x = robot.x
                piece.y = robot.y

    def _raycast_distance(self, robot: RobotState) -> float:
        """Simple raycast from robot in heading direction."""
        fc = self.state.field_config
        if not fc:
            return 9999
        rad = math.radians(robot.heading)
        step = 50
        for i in range(1, 200):
            px = robot.x + step * i * math.cos(rad)
            py = robot.y + step * i * math.sin(rad)
            # Check field boundary
            if px < 0 or px > fc.field_width or py < 0 or py > fc.field_height:
                return step * i
            # Check obstacles
            for obs in fc.obstacles:
                if obs.x <= px <= obs.x + obs.width and obs.y <= py <= obs.y + obs.height:
                    return step * i
        return 9999

    # === AI robots ===

    def _tick_ai_robots(self, dt: float) -> None:
        """Simple AI: find nearest uncollected piece → go grab → deliver to zone."""
        for robot in self.state.robots.values():
            if robot.is_player:
                continue
            if robot.holding:
                self._ai_deliver(robot, dt)
            else:
                self._ai_collect(robot, dt)

    def _ai_collect(self, robot: RobotState, dt: float) -> None:
        target_piece = self._find_nearest_piece(robot.x, robot.y, 99999)
        if not target_piece:
            return
        dx = target_piece.x - robot.x
        dy = target_piece.y - robot.y
        dist = math.hypot(dx, dy)
        if dist < PICKUP_RANGE_MM:
            target_piece.collected_by = robot.id
            robot.holding = target_piece.id
            return
        # Move towards piece
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        robot.heading = target_angle
        move = min(AI_SPEED * dt, dist)
        rad = math.radians(robot.heading)
        robot.trail.append((robot.x, robot.y))
        robot.x += move * math.cos(rad)
        robot.y += move * math.sin(rad)
        robot.x, robot.y = self._clamp_position(robot.x, robot.y)
        self._update_held_piece(robot)

    def _ai_deliver(self, robot: RobotState, dt: float) -> None:
        fc = self.state.field_config
        if not fc or not fc.scoring_zones:
            return
        # Find nearest scoring zone for this alliance
        best_zone = None
        best_dist = 99999.0
        for zone in fc.scoring_zones:
            if zone.alliance == robot.alliance or zone.alliance == Alliance.NEUTRAL:
                cx = zone.x + zone.width / 2
                cy = zone.y + zone.height / 2
                d = math.hypot(cx - robot.x, cy - robot.y)
                if d < best_dist:
                    best_dist = d
                    best_zone = zone
        if not best_zone:
            return
        cx = best_zone.x + best_zone.width / 2
        cy = best_zone.y + best_zone.height / 2
        dx = cx - robot.x
        dy = cy - robot.y
        dist = math.hypot(dx, dy)
        if dist < 200:
            # Release in zone
            piece = self._get_piece_by_id(robot.holding)
            if piece:
                piece.collected_by = None
                piece.x = robot.x
                piece.y = robot.y
                piece.in_zone = best_zone.id
                alliance_key = robot.alliance.value
                points = piece.value * best_zone.multiplier
                self.state.scores[alliance_key] = self.state.scores.get(alliance_key, 0) + points
                robot.score += points
            robot.holding = None
            return
        # Move towards zone
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        robot.heading = target_angle
        move = min(AI_SPEED * dt, dist)
        rad = math.radians(robot.heading)
        robot.trail.append((robot.x, robot.y))
        robot.x += move * math.cos(rad)
        robot.y += move * math.sin(rad)
        robot.x, robot.y = self._clamp_position(robot.x, robot.y)
        self._update_held_piece(robot)
