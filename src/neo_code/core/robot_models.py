"""Data models for Robot Arena - FGC 2D robot competition simulator."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class RobotCommandType(Enum):
    """Robot command types sent from student code via proxy."""
    FORWARD = auto()
    BACKWARD = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    STOP = auto()
    GRAB = auto()
    RELEASE = auto()
    SHOOT = auto()
    DISTANCE_SENSOR = auto()
    COLOR_SENSOR = auto()
    GET_POSITION = auto()
    GET_HEADING = auto()
    GET_MATCH_TIME = auto()
    GET_SCORE = auto()
    GET_ALLIES = auto()
    GET_OPPONENTS = auto()
    SET_STRATEGY = auto()
    ARENA_INIT = auto()


class PieceType(Enum):
    """Game piece shapes."""
    BALL = auto()
    CUBE = auto()
    CYLINDER = auto()


class Alliance(Enum):
    """Team alliance colors."""
    RED = "red"
    BLUE = "blue"
    NEUTRAL = "neutral"


class ObstacleShape(Enum):
    """Obstacle geometric shapes."""
    RECT = auto()
    CIRCLE = auto()


@dataclass
class RobotCommand:
    """A single robot command from student code."""
    command_type: RobotCommandType
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    robot_id: str = "player"


@dataclass
class GamePiece:
    """A game piece on the field."""
    id: str
    type: PieceType
    x: float
    y: float
    color: str = "#FFD700"
    value: int = 1
    label: str = ""
    collected_by: Optional[str] = None
    in_zone: Optional[str] = None


class MissionObjectiveType(Enum):
    """Types of mission objectives for training fields."""
    MOVE_TO = auto()          # Di den toa do
    GRAB_PIECE = auto()       # Nhat piece cu the
    RELEASE_IN_ZONE = auto()  # Tha trong zone
    SCORE_POINTS = auto()     # Dat N diem
    COLLECT_N = auto()        # Thu thap N piece


@dataclass
class MissionObjective:
    """A single objective within a mission."""
    id: str
    order: int                # Thu tu hien thi (1, 2, 3...)
    description: str          # "Di den Bong Do"
    description_en: str = ""
    objective_type: MissionObjectiveType = MissionObjectiveType.MOVE_TO
    target_piece_id: str = ""
    target_zone_id: str = ""
    target_x: float = 0.0
    target_y: float = 0.0
    target_radius: float = 500.0
    target_score: int = 0
    target_count: int = 0
    completed: bool = False
    hint: str = ""


@dataclass
class FieldMission:
    """A mission consisting of ordered objectives."""
    id: str
    name: str                 # "Thu thap qua bong"
    name_en: str = ""
    objectives: list[MissionObjective] = field(default_factory=list)


@dataclass
class ScoringZone:
    """A scoring zone on the field."""
    id: str
    x: float
    y: float
    width: float
    height: float
    color: str = "#00FF00"
    alliance: Alliance = Alliance.NEUTRAL
    multiplier: int = 1
    label: str = ""


@dataclass
class Obstacle:
    """A physical obstacle on the field."""
    id: str
    x: float
    y: float
    width: float
    height: float
    shape: ObstacleShape = ObstacleShape.RECT
    color: str = "#666666"


@dataclass
class RobotState:
    """State of a single robot on the field."""
    id: str
    x: float = 0.0
    y: float = 0.0
    heading: float = 0.0  # degrees, 0 = right/east
    alliance: Alliance = Alliance.RED
    is_player: bool = False
    holding: Optional[str] = None  # piece id
    trail: list[tuple[float, float]] = field(default_factory=list)
    score: int = 0


@dataclass
class FieldConfig:
    """Configuration for a specific FGC game field."""
    id: str
    name: str
    year: int
    description: str = ""
    field_width: float = 7000.0   # mm
    field_height: float = 7000.0  # mm
    game_pieces: list[GamePiece] = field(default_factory=list)
    scoring_zones: list[ScoringZone] = field(default_factory=list)
    obstacles: list[Obstacle] = field(default_factory=list)
    robot_start_positions: dict[str, tuple[float, float, float]] = field(default_factory=dict)
    match_duration: int = 150  # seconds
    missions: list[FieldMission] = field(default_factory=list)
    is_training: bool = False


@dataclass
class ArenaState:
    """Full state of the arena during a match."""
    field_config: Optional[FieldConfig] = None
    robots: dict[str, RobotState] = field(default_factory=dict)
    game_pieces: list[GamePiece] = field(default_factory=list)
    scores: dict[str, int] = field(default_factory=lambda: {"red": 0, "blue": 0})
    time_remaining: float = 150.0
    match_running: bool = False
    feedback_queue: list[dict] = field(default_factory=list)
    completed_objectives: list[str] = field(default_factory=list)
    active_mission: Optional[FieldMission] = None
