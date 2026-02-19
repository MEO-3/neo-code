"""FGC field configurations and robot educational projects.

Contains 7 FIRST Global Challenge field configs (2017-2025)
and 3 robot challenge projects with 3 difficulty levels each.
"""
from __future__ import annotations

from neo_code.core.robot_models import (
    FieldConfig, GamePiece, ScoringZone, Obstacle,
    PieceType, Alliance, ObstacleShape,
    FieldMission, MissionObjective, MissionObjectiveType,
)
from neo_code.education.projects import Project, ProjectLevel


# ══════════════════════════════════════════
# Category name
# ══════════════════════════════════════════
CAT_ROBOT = "Robot Arena"
CAT_ROBOT_EN = "Robot Arena"


# ══════════════════════════════════════════
# Training Fields (simple, with missions)
# ══════════════════════════════════════════

def _field_training_basic() -> FieldConfig:
    """San tap co ban: Di chuyen, nhat va ghi diem."""
    pieces = [
        GamePiece(id="ball_red", type=PieceType.BALL,
                  x=1500, y=2000, color="#ef4444", value=1, label="Bong Do"),
        GamePiece(id="ball_blue", type=PieceType.BALL,
                  x=2200, y=1000, color="#3b82f6", value=1, label="Bong Xanh"),
    ]
    zones = [
        ScoringZone(id="score_zone", x=2200, y=2200, width=600, height=600,
                    color="#22c55e", alliance=Alliance.NEUTRAL, multiplier=1,
                    label="Vung Ghi Diem"),
    ]
    starts = {"player": (500.0, 500.0, 0.0)}
    missions = [
        FieldMission(
            id="basic_mission", name="Hoc co ban", name_en="Learn Basics",
            objectives=[
                MissionObjective(
                    id="move_to_ball", order=1,
                    description="Di den Bong Do",
                    description_en="Move to Red Ball",
                    objective_type=MissionObjectiveType.MOVE_TO,
                    target_x=1500, target_y=2000, target_radius=400,
                    hint="r.forward(1000) de tien 1000mm",
                ),
                MissionObjective(
                    id="grab_ball", order=2,
                    description="Nhat Bong Do",
                    description_en="Grab Red Ball",
                    objective_type=MissionObjectiveType.GRAB_PIECE,
                    target_piece_id="ball_red",
                    hint="r.grab() khi o gan bong",
                ),
                MissionObjective(
                    id="score_it", order=3,
                    description="Mang den Vung Ghi Diem",
                    description_en="Deliver to Score Zone",
                    objective_type=MissionObjectiveType.RELEASE_IN_ZONE,
                    target_zone_id="score_zone",
                    hint="Di den vung xanh roi r.release()",
                ),
            ],
        ),
    ]
    return FieldConfig(
        id="training_basic", name="San Tap Co Ban", year=2025,
        description="San nho 3x3m. Hoc di chuyen, nhat va ghi diem.",
        field_width=3000, field_height=3000,
        game_pieces=pieces, scoring_zones=zones,
        robot_start_positions=starts,
        match_duration=999, missions=missions, is_training=True,
    )


def _field_training_collect() -> FieldConfig:
    """San tap thu thap: Nhieu vat pham, chon zone diem cao."""
    pieces = [
        GamePiece(id="ball_1", type=PieceType.BALL,
                  x=1000, y=3500, color="#ef4444", value=1, label="Bong 1"),
        GamePiece(id="ball_2", type=PieceType.BALL,
                  x=3500, y=3500, color="#3b82f6", value=1, label="Bong 2"),
        GamePiece(id="cube_1", type=PieceType.CUBE,
                  x=2500, y=1500, color="#eab308", value=2, label="Cube Vang"),
        GamePiece(id="cube_2", type=PieceType.CUBE,
                  x=1500, y=2500, color="#22c55e", value=2, label="Cube Xanh"),
    ]
    zones = [
        ScoringZone(id="zone_x1", x=200, y=200, width=800, height=800,
                    color="#ef4444", alliance=Alliance.NEUTRAL, multiplier=1,
                    label="Zone x1"),
        ScoringZone(id="zone_x2", x=4000, y=4000, width=800, height=800,
                    color="#eab308", alliance=Alliance.NEUTRAL, multiplier=2,
                    label="Zone x2"),
    ]
    starts = {"player": (500.0, 500.0, 0.0)}
    missions = [
        FieldMission(
            id="collect_mission", name="Thu thap vat pham",
            name_en="Collect Items",
            objectives=[
                MissionObjective(
                    id="grab_any", order=1,
                    description="Nhat bat ky vat nao",
                    description_en="Grab any item",
                    objective_type=MissionObjectiveType.GRAB_PIECE,
                    hint="Di toi vat gan nhat roi r.grab()",
                ),
                MissionObjective(
                    id="score_1", order=2,
                    description="Ghi duoc 1 diem",
                    description_en="Score 1 point",
                    objective_type=MissionObjectiveType.SCORE_POINTS,
                    target_score=1,
                    hint="Tha vat trong zone de ghi diem",
                ),
                MissionObjective(
                    id="score_5", order=3,
                    description="Ghi duoc 5 diem",
                    description_en="Score 5 points",
                    objective_type=MissionObjectiveType.SCORE_POINTS,
                    target_score=5,
                    hint="Zone x2 cho gap doi diem! Cube = 2 diem",
                ),
            ],
        ),
    ]
    return FieldConfig(
        id="training_collect", name="San Tap Thu Thap", year=2025,
        description="San 5x5m. Thu thap nhieu vat, chon zone diem cao.",
        field_width=5000, field_height=5000,
        game_pieces=pieces, scoring_zones=zones,
        robot_start_positions=starts,
        match_duration=999, missions=missions, is_training=True,
    )


def _field_training_match() -> FieldConfig:
    """San tap thi dau: 1v1 voi AI."""
    pieces = [
        GamePiece(id=f"match_ball_{i}", type=PieceType.BALL,
                  x=1500 + (i % 3) * 2000, y=2000 + (i // 3) * 3000,
                  color=["#ef4444", "#3b82f6", "#eab308",
                         "#22c55e", "#a855f7", "#f97316"][i],
                  value=1, label=f"Bong {i+1}")
        for i in range(6)
    ]
    zones = [
        ScoringZone(id="red_zone", x=200, y=2500, width=1200, height=2000,
                    color="#ef4444", alliance=Alliance.RED, multiplier=1,
                    label="RED Zone"),
        ScoringZone(id="blue_zone", x=5600, y=2500, width=1200, height=2000,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=1,
                    label="BLUE Zone"),
        ScoringZone(id="center_zone", x=2800, y=2800, width=1400, height=1400,
                    color="#22c55e", alliance=Alliance.NEUTRAL, multiplier=2,
                    label="Center x2"),
    ]
    starts = {
        "player": (1000.0, 1000.0, 0.0),
        "blue_1": (6000.0, 6000.0, 180.0),
    }
    missions = [
        FieldMission(
            id="match_mission", name="Thi dau 1v1",
            name_en="1v1 Match",
            objectives=[
                MissionObjective(
                    id="grab_first", order=1,
                    description="Nhat bong dau tien",
                    description_en="Grab first ball",
                    objective_type=MissionObjectiveType.GRAB_PIECE,
                    hint="Nhanh len truoc AI!",
                ),
                MissionObjective(
                    id="score_3", order=2,
                    description="Ghi 3 diem",
                    description_en="Score 3 points",
                    objective_type=MissionObjectiveType.SCORE_POINTS,
                    target_score=3,
                    hint="Center x2 cho gap doi!",
                ),
                MissionObjective(
                    id="win", order=3,
                    description="Thang tran dau",
                    description_en="Win the match",
                    objective_type=MissionObjectiveType.SCORE_POINTS,
                    target_score=4,
                    hint="Thu thap nhieu va ghi diem nhanh!",
                ),
            ],
        ),
    ]
    return FieldConfig(
        id="training_match", name="San Tap Thi Dau", year=2025,
        description="San 7x7m. Thi dau 1v1 voi AI trong 120 giay.",
        field_width=7000, field_height=7000,
        game_pieces=pieces, scoring_zones=zones,
        robot_start_positions=starts,
        match_duration=120, missions=missions, is_training=True,
    )


# ══════════════════════════════════════════
# FGC Field Configurations (7000x7000mm, 3v3, 150s)
# ══════════════════════════════════════════

def _field_eco_equilibrium_2025() -> FieldConfig:
    """2025 - Eco Equilibrium: Da dang sinh hoc."""
    _labels = ["Do", "Xanh", "La", "Vang", "Tim"]
    pieces = [
        GamePiece(id=f"ball_{i}", type=PieceType.BALL,
                  x=2500 + (i % 5) * 500, y=2500 + (i // 5) * 500,
                  color=["#ef4444", "#3b82f6", "#22c55e", "#eab308", "#a855f7"][i % 5],
                  value=1, label=f"{_labels[i % 5]} {i+1}")
        for i in range(10)
    ]
    zones = [
        ScoringZone(id="red_zone", x=200, y=2500, width=1200, height=2000,
                    color="#ef4444", alliance=Alliance.RED, multiplier=1, label="RED Zone"),
        ScoringZone(id="blue_zone", x=5600, y=2500, width=1200, height=2000,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=1, label="BLUE Zone"),
        ScoringZone(id="shared_zone", x=2800, y=2800, width=1400, height=1400,
                    color="#22c55e", alliance=Alliance.NEUTRAL, multiplier=3,
                    label="SHARED x3"),
    ]
    starts = {
        "player": (1000.0, 1000.0, 0.0),
        "red_1": (1000.0, 6000.0, 0.0),
        "red_2": (500.0, 3500.0, 0.0),
        "blue_1": (6000.0, 1000.0, 180.0),
        "blue_2": (6000.0, 6000.0, 180.0),
        "blue_3": (6500.0, 3500.0, 180.0),
    }
    return FieldConfig(
        id="eco_equilibrium_2025", name="Eco Equilibrium 2025", year=2025,
        description="Da dang sinh hoc - Thu thap cac qua bong mau va giao den zone. Shared zone x3 diem!",
        game_pieces=pieces, scoring_zones=zones, robot_start_positions=starts,
    )


def _field_feeding_future_2024() -> FieldConfig:
    """2024 - Feeding the Future: An ninh luong thuc."""
    _labels = ["Nuoc", "Nang luong", "Thuc pham"]
    pieces = [
        GamePiece(id=f"cube_{i}", type=PieceType.CUBE,
                  x=1500 + (i % 4) * 1200, y=2000 + (i // 4) * 1500,
                  color=["#3b82f6", "#eab308", "#22c55e"][i % 3],
                  value=2, label=f"{_labels[i % 3]} {i+1}")
        for i in range(8)
    ]
    zones = [
        ScoringZone(id="red_farm", x=200, y=200, width=1500, height=1500,
                    color="#ef4444", alliance=Alliance.RED, multiplier=1, label="RED Farm"),
        ScoringZone(id="blue_farm", x=5300, y=5300, width=1500, height=1500,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=1, label="BLUE Farm"),
    ]
    obstacles = [
        Obstacle(id="river", x=3200, y=0, width=600, height=7000,
                 color="#1e40af"),
    ]
    starts = {
        "player": (1000.0, 3500.0, 0.0),
        "red_1": (1000.0, 5500.0, 0.0),
        "red_2": (1000.0, 1500.0, 0.0),
        "blue_1": (6000.0, 3500.0, 180.0),
        "blue_2": (6000.0, 5500.0, 180.0),
        "blue_3": (6000.0, 1500.0, 180.0),
    }
    return FieldConfig(
        id="feeding_future_2024", name="Feeding the Future 2024", year=2024,
        description="An ninh luong thuc - Thu thap cube nuoc/nang luong/thuc pham. Canh chung: song!",
        game_pieces=pieces, scoring_zones=zones, obstacles=obstacles,
        robot_start_positions=starts,
    )


def _field_hydrogen_horizons_2023() -> FieldConfig:
    """2023 - Hydrogen Horizons: Nang luong hydro."""
    pieces = [
        GamePiece(id=f"cyl_{i}", type=PieceType.CYLINDER,
                  x=1500 + (i % 5) * 900, y=2000 + (i // 5) * 1500,
                  color="#06b6d4", value=1, label=f"Hydro {i+1}")
        for i in range(10)
    ]
    zones = [
        ScoringZone(id="red_reactor", x=200, y=2500, width=1000, height=2000,
                    color="#ef4444", alliance=Alliance.RED, multiplier=3, label="RED Reactor x3"),
        ScoringZone(id="blue_reactor", x=5800, y=2500, width=1000, height=2000,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=3, label="BLUE Reactor x3"),
        ScoringZone(id="red_storage", x=200, y=500, width=1500, height=1500,
                    color="#ef4444", alliance=Alliance.RED, multiplier=1, label="RED Storage"),
        ScoringZone(id="blue_storage", x=5300, y=5000, width=1500, height=1500,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=1, label="BLUE Storage"),
    ]
    starts = {
        "player": (800.0, 1000.0, 0.0),
        "red_1": (800.0, 6000.0, 0.0),
        "red_2": (500.0, 3500.0, 0.0),
        "blue_1": (6200.0, 1000.0, 180.0),
        "blue_2": (6200.0, 6000.0, 180.0),
        "blue_3": (6500.0, 3500.0, 180.0),
    }
    return FieldConfig(
        id="hydrogen_horizons_2023", name="Hydrogen Horizons 2023", year=2023,
        description="Nang luong hydro - Thu thap ong hydro va giao den reactor zone (x3 diem)!",
        game_pieces=pieces, scoring_zones=zones, robot_start_positions=starts,
    )


def _field_carbon_capture_2022() -> FieldConfig:
    """2022 - Carbon Capture: Bat giu CO2."""
    pieces = [
        GamePiece(id=f"co2_{i}", type=PieceType.BALL,
                  x=1000 + (i % 4) * 1500, y=1500 + (i // 4) * 2000,
                  color="#374151", value=2, label=f"CO2 {i+1}")
        for i in range(8)
    ]
    zones = [
        ScoringZone(id="red_capture", x=200, y=2500, width=1200, height=2000,
                    color="#ef4444", alliance=Alliance.RED, multiplier=1, label="RED Capture"),
        ScoringZone(id="blue_capture", x=5600, y=2500, width=1200, height=2000,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=1, label="BLUE Capture"),
    ]
    obstacles = [
        Obstacle(id="center_wall", x=3200, y=2000, width=600, height=3000,
                 color="#6b7280"),
    ]
    starts = {
        "player": (1000.0, 1000.0, 0.0),
        "red_1": (1000.0, 6000.0, 0.0),
        "red_2": (500.0, 3500.0, 0.0),
        "blue_1": (6000.0, 1000.0, 180.0),
        "blue_2": (6000.0, 6000.0, 180.0),
        "blue_3": (6500.0, 3500.0, 180.0),
    }
    return FieldConfig(
        id="carbon_capture_2022", name="Carbon Capture 2022", year=2022,
        description="Bat giu CO2 - Thu thap bong CO2 toi va di chuyen qua tuong giua san!",
        game_pieces=pieces, scoring_zones=zones, obstacles=obstacles,
        robot_start_positions=starts,
    )


def _field_ocean_opportunities_2019() -> FieldConfig:
    """2019 - Ocean Opportunities: O nhiem dai duong."""
    _labels = ["Do", "Cam", "Vang", "La", "Xanh", "Tim"]
    pieces = [
        GamePiece(id=f"trash_{i}", type=PieceType.BALL,
                  x=1000 + (i % 4) * 1400, y=1000 + (i // 4) * 1700,
                  color=["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6", "#8b5cf6"][i % 6],
                  value=1, label=f"Rac {_labels[i % 6]} {i+1}")
        for i in range(12)
    ]
    zones = [
        ScoringZone(id="red_shore", x=200, y=200, width=1500, height=2000,
                    color="#ef4444", alliance=Alliance.RED, multiplier=1, label="RED Shore"),
        ScoringZone(id="blue_shore", x=5300, y=4800, width=1500, height=2000,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=1, label="BLUE Shore"),
        ScoringZone(id="recycle_center", x=2800, y=2800, width=1400, height=1400,
                    color="#22c55e", alliance=Alliance.NEUTRAL, multiplier=2,
                    label="Recycle x2"),
    ]
    starts = {
        "player": (800.0, 3500.0, 0.0),
        "red_1": (800.0, 5500.0, 0.0),
        "red_2": (800.0, 1500.0, 0.0),
        "blue_1": (6200.0, 3500.0, 180.0),
        "blue_2": (6200.0, 5500.0, 180.0),
        "blue_3": (6200.0, 1500.0, 180.0),
    }
    return FieldConfig(
        id="ocean_opportunities_2019", name="Ocean Opportunities 2019", year=2019,
        description="O nhiem dai duong - Don rac tu dai duong! Recycle center x2 diem.",
        game_pieces=pieces, scoring_zones=zones, robot_start_positions=starts,
    )


def _field_energy_impact_2018() -> FieldConfig:
    """2018 - Energy Impact: Nang luong tai tao."""
    _labels = ["Mat troi", "Gio"]
    pieces = [
        GamePiece(id=f"energy_{i}", type=PieceType.CUBE,
                  x=1500 + (i % 4) * 1200, y=2000 + (i // 4) * 1500,
                  color=["#eab308", "#22c55e"][i % 2], value=2,
                  label=f"{_labels[i % 2]} {i+1}")
        for i in range(8)
    ]
    zones = [
        ScoringZone(id="solar_zone", x=2500, y=5500, width=2000, height=1200,
                    color="#eab308", alliance=Alliance.NEUTRAL, multiplier=2,
                    label="Solar x2"),
        ScoringZone(id="wind_zone", x=2500, y=300, width=2000, height=1200,
                    color="#22c55e", alliance=Alliance.NEUTRAL, multiplier=2,
                    label="Wind x2"),
        ScoringZone(id="red_base", x=200, y=2500, width=1200, height=2000,
                    color="#ef4444", alliance=Alliance.RED, multiplier=1, label="RED Base"),
        ScoringZone(id="blue_base", x=5600, y=2500, width=1200, height=2000,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=1, label="BLUE Base"),
    ]
    starts = {
        "player": (1000.0, 1000.0, 0.0),
        "red_1": (1000.0, 6000.0, 0.0),
        "red_2": (500.0, 3500.0, 0.0),
        "blue_1": (6000.0, 1000.0, 180.0),
        "blue_2": (6000.0, 6000.0, 180.0),
        "blue_3": (6500.0, 3500.0, 180.0),
    }
    return FieldConfig(
        id="energy_impact_2018", name="Energy Impact 2018", year=2018,
        description="Nang luong tai tao - Thu thap cube nang luong. Solar/Wind zone x2 diem!",
        game_pieces=pieces, scoring_zones=zones, robot_start_positions=starts,
    )


def _field_h2o_flow_2017() -> FieldConfig:
    """2017 - H2O Flow: Loc nuoc."""
    _labels = ["Xanh", "Do", "La", "Vang", "Tim"]
    pieces = [
        GamePiece(id=f"water_{i}", type=PieceType.BALL,
                  x=1200 + (i % 5) * 1000, y=1500 + (i // 5) * 2000,
                  color=["#3b82f6", "#ef4444", "#22c55e", "#eab308", "#a855f7"][i % 5],
                  value=1, label=f"Nuoc {_labels[i % 5]} {i+1}")
        for i in range(10)
    ]
    zones = [
        ScoringZone(id="red_filter", x=200, y=2500, width=1200, height=2000,
                    color="#ef4444", alliance=Alliance.RED, multiplier=1, label="RED Filter"),
        ScoringZone(id="blue_filter", x=5600, y=2500, width=1200, height=2000,
                    color="#3b82f6", alliance=Alliance.BLUE, multiplier=1, label="BLUE Filter"),
        ScoringZone(id="clean_zone", x=2800, y=5500, width=1400, height=1200,
                    color="#06b6d4", alliance=Alliance.NEUTRAL, multiplier=2,
                    label="Clean x2"),
    ]
    obstacles = [
        Obstacle(id="dam", x=3000, y=1500, width=1000, height=500,
                 color="#8b7355"),
    ]
    starts = {
        "player": (1000.0, 1000.0, 0.0),
        "red_1": (1000.0, 6000.0, 0.0),
        "red_2": (500.0, 3500.0, 0.0),
        "blue_1": (6000.0, 1000.0, 180.0),
        "blue_2": (6000.0, 6000.0, 180.0),
        "blue_3": (6500.0, 3500.0, 180.0),
    }
    return FieldConfig(
        id="h2o_flow_2017", name="H2O Flow 2017", year=2017,
        description="Loc nuoc - Thu thap bong nuoc mau va loc qua dam! Clean zone x2 diem.",
        game_pieces=pieces, scoring_zones=zones, obstacles=obstacles,
        robot_start_positions=starts,
    )


# ══════════════════════════════════════════
# Field registry
# ══════════════════════════════════════════

_FIELD_BUILDERS = {
    # Training fields
    "training_basic": _field_training_basic,
    "training_collect": _field_training_collect,
    "training_match": _field_training_match,
    # FGC competition fields
    "eco_equilibrium_2025": _field_eco_equilibrium_2025,
    "feeding_future_2024": _field_feeding_future_2024,
    "hydrogen_horizons_2023": _field_hydrogen_horizons_2023,
    "carbon_capture_2022": _field_carbon_capture_2022,
    "ocean_opportunities_2019": _field_ocean_opportunities_2019,
    "energy_impact_2018": _field_energy_impact_2018,
    "h2o_flow_2017": _field_h2o_flow_2017,
}


def get_field_config(field_id: str) -> FieldConfig | None:
    """Get a field config by ID."""
    builder = _FIELD_BUILDERS.get(field_id)
    return builder() if builder else None


def get_all_field_configs() -> list[FieldConfig]:
    """Get all available field configs."""
    return [builder() for builder in _FIELD_BUILDERS.values()]


def get_field_ids() -> list[str]:
    """Get all available field IDs."""
    return list(_FIELD_BUILDERS.keys())


# ══════════════════════════════════════════
# Robot Challenge Projects (3 projects, 3 levels each)
# ══════════════════════════════════════════

ROBOT_PROJECTS: list[Project] = [
    # ── Training Projects (with field_id) ──
    Project(
        id="robot_training_basic",
        title="San tap: Di chuyen & Nhat do",
        title_en="Training: Move & Grab",
        category=CAT_ROBOT,
        category_en=CAT_ROBOT_EN,
        description="Hoc cach dieu khien robot di chuyen, nhat va ghi diem tren san tap nho.",
        description_en="Learn to move, grab, and score on a small training field.",
        concepts=["robot", "forward", "turn", "grab", "release", "scoring"],
        field_id="training_basic",
        solution='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO SAN TAP CO BAN (3000x3000mm)
# ==============================
# Robot (Ban) tai: (500, 500) - goc duoi trai
# Bong Do tai: (1500, 2000) - giua san
# Bong Xanh tai: (2200, 1000) - ben phai
# Vung Ghi Diem tai: (2200, 2200) - goc tren phai
# ==============================

# BUOC 1: Di den Bong Do
r.forward(1000)       # Tien sang phai 1000mm -> (1500, 500)
r.turn_left(90)       # Quay trai 90 do (huong len)
r.forward(1500)       # Tien len 1500mm -> (1500, 2000)

# BUOC 2: Nhat Bong Do
r.grab()              # Nhat bong gan nhat

# BUOC 3: Di den Vung Ghi Diem
r.turn_right(90)      # Quay phai (huong sang phai)
r.forward(1000)       # Tien sang phai 1000mm -> (2500, 2000)
r.turn_left(90)       # Quay trai (huong len)
r.forward(500)        # Tien len 500mm -> (2500, 2500)

# BUOC 4: Tha de ghi diem!
r.release()           # Tha bong -> +1 diem!
''',
        levels={
            1: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO SAN TAP CO BAN (3000x3000mm)
# ==============================
# Robot (Ban) tai: (500, 500) - goc duoi trai
# Bong Do tai: (1500, 2000) - giua san
# Bong Xanh tai: (2200, 1000) - ben phai
# Vung Ghi Diem tai: (2200, 2200) - goc tren phai
# ==============================

# BUOC 1: Di den Bong Do
r.forward(1000)       # Tien sang phai 1000mm
r.turn_left(90)       # Quay trai 90 do (huong len)
r.forward(1500)       # Tien len 1500mm

# BUOC 2: Nhat Bong Do
r.grab()              # Nhat bong gan nhat

# BUOC 3: Di den Vung Ghi Diem
# Hay thay doi khoang cach de robot di den vung xanh!
r.turn_right(90)      # Quay phai (huong sang phai)
r.forward(1000)       # Tien sang phai 1000mm
r.turn_left(90)       # Quay trai (huong len)
r.forward(500)        # Tien len 500mm

# BUOC 4: Tha de ghi diem!
r.release()           # +1 diem!
''',
                hints=[
                    "Thay doi so trong forward() de robot di xa hon hoac gan hon",
                    "Xem ban do o tren de biet toa do",
                ],
            ),
            2: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO SAN TAP CO BAN (3000x3000mm)
# ==============================
# Robot (Ban) tai: (500, 500) - goc duoi trai
# Bong Do tai: (1500, 2000) - giua san
# Vung Ghi Diem tai: (2200, 2200) - goc tren phai
# ==============================

# BUOC 1: Di den Bong Do
r.forward(___)        # Tien sang phai bao nhieu mm?
r.turn_left(___)      # Quay trai bao nhieu do?
r.forward(___)        # Tien len bao nhieu mm?

# BUOC 2: Nhat Bong Do
r.___()               # Lenh gi de nhat?

# BUOC 3: Di den Vung Ghi Diem
r.turn_right(90)      # Quay phai (huong sang phai)
r.forward(1000)       # Tien sang phai
r.turn_left(90)       # Quay trai (huong len)
r.forward(500)        # Tien len

# BUOC 4: Tha de ghi diem!
r.___()               # Lenh gi de tha?
''',
                hints=[
                    "forward(1000) de tien 1000mm sang phai",
                    "turn_left(90) de quay len tren",
                    "grab() de nhat, release() de tha",
                ],
            ),
            3: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO SAN TAP CO BAN (3000x3000mm)
# ==============================
# Robot (Ban) tai: (500, 500) - goc duoi trai
# Bong Do tai: (1500, 2000) - giua san
# Bong Xanh tai: (2200, 1000) - ben phai
# Vung Ghi Diem tai: (2200, 2200) - goc tren phai
# ==============================

# Nhiem vu: Nhat Bong Do va mang den Vung Ghi Diem!
# BUOC 1: Di den bong (dung forward + turn_left)
# BUOC 2: Nhat bong (dung grab)
# BUOC 3: Di den vung xanh
# BUOC 4: Tha bong (dung release)
''',
                hints=[
                    "r.forward(mm) de tien, r.turn_left(do) de quay",
                    "r.grab() khi dung gan bong (300mm)",
                    "r.release() khi dung trong Vung Ghi Diem",
                ],
            ),
        },
    ),

    Project(
        id="robot_training_collect",
        title="San tap: Thu thap vat pham",
        title_en="Training: Collect Items",
        category=CAT_ROBOT,
        category_en=CAT_ROBOT_EN,
        description="San lon hon voi 4 vat pham va 2 zone diem khac nhau. Hoc chon zone diem cao!",
        description_en="Larger field with 4 items and 2 scoring zones. Learn to choose high-score zones!",
        concepts=["robot", "grab", "release", "scoring", "strategy", "loop"],
        field_id="training_collect",
        solution='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO THU THAP (5000x5000mm)
# ==============================
# Robot tai: (500, 500) - goc duoi trai
# Bong 1 tai: (1000, 3500) - tren trai
# Bong 2 tai: (3500, 3500) - tren phai
# Cube Vang tai: (2500, 1500) - giua duoi
# Cube Xanh tai: (1500, 2500) - giua trai
# Zone x1 tai: (200, 200) - goc duoi trai
# Zone x2 tai: (4000, 4000) - goc tren phai (DIEM GAP DOI!)
# ==============================

# BUOC 1: Nhat Cube Xanh (2 diem vi cube = value 2)
r.forward(1000)       # Tien sang phai
r.turn_left(90)       # Quay len
r.forward(2000)       # Tien len den Cube Xanh
r.grab()              # Nhat Cube Xanh!

# BUOC 2: Mang den Zone x2 (diem x2 = 4 diem!)
r.turn_right(45)      # Quay cheo sang phai
r.forward(2800)       # Tien den Zone x2
r.release()           # +4 diem! (2 x 2)

# BUOC 3: Quay lai nhat Bong 2
r.turn_right(135)     # Quay xuong
r.forward(700)
r.grab()              # Nhat Bong 2

# BUOC 4: Ghi diem tai Zone x2
r.turn_left(135)
r.forward(700)
r.release()           # +2 diem! (1 x 2)
''',
        levels={
            1: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO THU THAP (5000x5000mm)
# ==============================
# Robot tai: (500, 500) - goc duoi trai
# Bong 1 tai: (1000, 3500) - tren trai
# Cube Vang tai: (2500, 1500) - giua
# Zone x1 tai: (200, 200) - goc duoi trai
# Zone x2 tai: (4000, 4000) - goc tren phai (GAP DOI!)
# ==============================

# BUOC 1: Nhat Cube Vang
r.forward(2000)       # Tien sang phai
r.turn_left(90)       # Quay len
r.forward(1000)       # Tien len den Cube Vang
r.grab()              # Nhat!

# BUOC 2: Mang den Zone x2 (diem x2!)
r.turn_left(45)
r.forward(2800)
r.release()           # +4 diem!

# Thu them: nhat Bong 1 va ghi diem!
# Hay thay doi code ben duoi
r.turn_left(135)
r.forward(1000)
r.grab()
r.turn_right(180)
r.forward(1000)
r.release()
''',
                hints=[
                    "Zone x2 cho gap doi diem!",
                    "Cube co value=2, Bong co value=1",
                ],
            ),
            2: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO THU THAP (5000x5000mm)
# ==============================
# Robot tai: (500, 500)
# Cube Xanh tai: (1500, 2500)
# Zone x2 tai: (4000, 4000) - GAP DOI!
# ==============================

# BUOC 1: Di den Cube Xanh
r.forward(___)
r.turn_left(___)
r.forward(___)

# BUOC 2: Nhat Cube
r.___()

# BUOC 3: Di den Zone x2
r.turn_right(45)
r.forward(___)

# BUOC 4: Tha de ghi diem
r.___()
''',
                hints=[
                    "forward(1000) sang phai, turn_left(90) quay len",
                    "grab() de nhat, release() de ghi diem",
                    "Zone x2 o goc tren phai (4000, 4000)",
                ],
            ),
            3: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO THU THAP (5000x5000mm)
# ==============================
# Robot tai: (500, 500) - goc duoi trai
# Bong 1 tai: (1000, 3500)    | value=1
# Bong 2 tai: (3500, 3500)    | value=1
# Cube Vang tai: (2500, 1500) | value=2
# Cube Xanh tai: (1500, 2500) | value=2
# Zone x1 tai: (200, 200)     | nhan x1
# Zone x2 tai: (4000, 4000)   | nhan x2 (GAP DOI!)
# ==============================

# Nhiem vu: Ghi it nhat 5 diem!
# Goi y: Cube (2 diem) + Zone x2 = 4 diem/lan!
''',
                hints=[
                    "Uu tien nhat Cube (value=2) va Zone x2",
                    "Cube tai Zone x2 = 2 * 2 = 4 diem!",
                    "Can 5 diem: 1 Cube x2 (4) + 1 Bong x1 (1) = 5",
                ],
            ),
        },
    ),

    Project(
        id="robot_training_match",
        title="San tap: Thi dau 1v1",
        title_en="Training: 1v1 Match",
        category=CAT_ROBOT,
        category_en=CAT_ROBOT_EN,
        description="Thi dau 1v1 voi robot AI trong 120 giay. Nhat bong va ghi diem nhieu hon doi thu!",
        description_en="Compete 1v1 against AI robot in 120 seconds. Grab balls and score more!",
        concepts=["robot", "strategy", "competition", "loop", "time management"],
        field_id="training_match",
        solution='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO THI DAU (7000x7000mm) - 120 giay
# ==============================
# Robot (Ban) tai: (1000, 1000) - goc duoi trai - RED
# AI (Doi thu) tai: (6000, 6000) - goc tren phai - BLUE
# 6 bong rai khap san
# RED Zone tai: (200, 2500) - ben trai
# BLUE Zone tai: (5600, 2500) - ben phai
# Center x2 tai: (2800, 2800) - GIUA SAN (GAP DOI!)
# ==============================

# Chien luoc: Rush Center x2 truoc!
r.set_strategy("aggressive")

# BUOC 1: Nhat bong gan nhat
r.forward(500)
r.turn_left(45)
r.forward(1200)
r.grab()              # Nhat Bong 1!

# BUOC 2: Ghi diem tai Center x2
r.turn_left(15)
r.forward(1500)
r.release()           # +2 diem (1 x 2)!

# BUOC 3: Thu thap them bang vong lap
for i in range(3):
    r.turn_right(90 + i * 30)
    r.forward(1500)
    r.grab()
    r.turn_right(180)
    r.forward(1500)
    r.release()       # +2 diem moi lan!
''',
        levels={
            1: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO THI DAU (7000x7000mm) - 120 giay
# ==============================
# Robot (Ban - RED) tai: (1000, 1000)
# AI (BLUE) tai: (6000, 6000)
# Center x2 tai: (2800, 2800) - GAP DOI!
# ==============================

r.set_strategy("aggressive")

# Rush den bong gan nhat
r.forward(500)
r.turn_left(45)
r.forward(1200)
r.grab()

# Ghi diem tai Center x2
r.turn_left(15)
r.forward(1500)
r.release()           # +2!

# Thu thap them - hay them code!
for i in range(3):
    r.turn_right(90 + i * 30)
    r.forward(1500)
    r.grab()
    r.turn_right(180)
    r.forward(1500)
    r.release()
''',
                hints=["Thu thay doi strategy va huong di de thang AI!"],
            ),
            2: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO THI DAU (7000x7000mm)
# ==============================
# Robot (RED) tai: (1000, 1000)
# AI (BLUE) tai: (6000, 6000)
# Center x2 tai giua san
# ==============================

r.set_strategy(___)

# Nhat bong dau tien
r.forward(500)
r.turn_left(45)
r.forward(1200)
r.___()               # Nhat bong!

# Ghi diem tai Center x2
r.turn_left(15)
r.forward(1500)
r.___()               # Ghi diem!

# Vong lap thu thap them
for i in range(___):
    r.turn_right(90 + i * 30)
    r.forward(___)
    r.___()
    r.turn_right(180)
    r.forward(___)
    r.___()
''',
                hints=[
                    '"aggressive" de choi tan cong',
                    "grab() nhat, release() ghi diem",
                    "Lap 3 vong de thu thap du bong",
                ],
            ),
            3: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO THI DAU (7000x7000mm) - 120 giay
# ==============================
# Robot (Ban - RED) tai: (1000, 1000) - goc duoi trai
# AI (Doi thu - BLUE) tai: (6000, 6000) - goc tren phai
# Bong 1-6 rai khap san
# RED Zone tai: (200, 2500) - ben trai
# BLUE Zone tai: (5600, 2500) - ben phai
# Center x2 tai: (2800, 2800) - GAP DOI!
# ==============================

# Nhiem vu: Thang AI! Ghi nhieu diem hon trong 120 giay
# Goi y:
#   - Center x2 cho gap doi diem
#   - Nhat nhanh truoc AI
#   - Dung vong lap for de thu thap nhieu
''',
                hints=[
                    "r.set_strategy('aggressive') de bat dau",
                    "Uu tien Center x2 de ghi nhieu diem",
                    "Dung for loop de grab/release nhieu lan",
                ],
            ),
        },
    ),

    # ── Original Projects (updated with field_id) ──
    Project(
        id="robot_first_move",
        title="Robot di chuyen dau tien",
        title_en="First Robot Movement",
        category=CAT_ROBOT,
        category_en=CAT_ROBOT_EN,
        description="Dieu khien robot di chuyen tren san dau. Hoc forward(), backward(), turn_left(), turn_right().",
        description_en="Control a robot on the arena. Learn forward(), backward(), turn_left(), turn_right().",
        concepts=["robot", "forward", "backward", "turn", "movement"],
        field_id="eco_equilibrium_2025",
        solution='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# Robot (Ban) tai: (1000, 1000) - goc duoi trai
# 10 bong mau o giua san (2500-4500, 2500-3000)
# RED Zone: ben trai | BLUE Zone: ben phai
# SHARED x3: giua san - GAP BA!
# ==============================

# BUOC 1: Di chuyen hinh vuong
for i in range(4):
    r.forward(500)    # Tien 500mm
    r.turn_left(90)   # Quay trai 90 do

# BUOC 2: Di chuyen zig-zag
r.forward(300)        # Tien 300mm
r.turn_right(45)      # Quay phai 45 do
r.forward(400)        # Tien cheo
r.turn_left(45)       # Quay lai thang
r.forward(300)        # Tien tiep
''',
        levels={
            1: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# Robot (Ban) tai: (1000, 1000) - goc duoi trai
# ==============================

# BUOC 1: Di hinh vuong
# Hay thay doi khoang cach (500) va goc quay (90)!
for i in range(4):
    r.forward(500)    # Tien 500mm
    r.turn_left(90)   # Quay trai 90 do
''',
                hints=["Thay doi 500 de robot di xa hon hoac gan hon"],
            ),
            2: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# Robot (Ban) tai: (1000, 1000)
# ==============================

# BUOC 1: Di hinh vuong - 4 lan tien va quay
for i in range(___):
    r.forward(___)    # Tien bao nhieu mm?
    r.turn_left(___) # Quay bao nhieu do?
''',
                hints=[
                    "Hinh vuong co 4 canh",
                    "Moi canh dai 500mm",
                    "Quay 90 do de tao goc vuong",
                ],
            ),
            3: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# Robot (Ban) tai: (1000, 1000) - goc duoi trai
# ==============================

# Nhiem vu: Dieu khien robot ve hinh vuong tren san
# Goi y: dung for loop, forward() va turn_left()
''',
                hints=[
                    "Dung for i in range(4):",
                    "r.forward(500) de tien 500mm",
                    "r.turn_left(90) de quay trai 90 do",
                ],
            ),
        },
    ),

    Project(
        id="robot_collect_pieces",
        title="Thu thap game piece",
        title_en="Collect Game Pieces",
        category=CAT_ROBOT,
        category_en=CAT_ROBOT_EN,
        description="Dung sensor de tim va thu thap game piece. Hoc grab(), release(), distance_sensor().",
        description_en="Use sensors to find and collect game pieces. Learn grab(), release(), distance_sensor().",
        concepts=["robot", "grab", "release", "sensor", "scoring"],
        field_id="eco_equilibrium_2025",
        solution='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# Robot (Ban) tai: (1000, 1000)
# Bong mau tai: (2500-4500, 2500-3000) - giua san
# RED Zone tai: (200, 2500) w=1200 h=2000
# SHARED x3 tai: (2800, 2800) w=1400 h=1400
# ==============================

# BUOC 1: Di den khu vuc co bong
r.forward(1500)       # Tien sang phai 1500mm
r.turn_left(45)       # Quay cheo len tren
r.forward(500)        # Tien 500mm

# BUOC 2: Nhat bong
r.grab()              # Nhat bong gan nhat!

# BUOC 3: Mang den RED Zone
r.turn_left(135)      # Quay ve ben trai
r.forward(2000)       # Tien 2000mm den RED Zone

# BUOC 4: Tha de ghi diem!
r.release()           # +1 diem!

# BUOC 5: Tim bong khac
r.turn_right(180)     # Quay nguoc lai
r.forward(1500)       # Tien ra giua san
r.turn_right(30)
r.forward(500)
r.grab()              # Nhat bong thu 2!

# BUOC 6: Ghi diem lan 2
r.turn_right(150)
r.forward(2000)
r.release()           # +1 diem nua!
''',
        levels={
            1: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# Robot tai: (1000, 1000)
# Bong tai: (2500-4500, 2500-3000)
# RED Zone tai: (200, 2500) - ben trai
# ==============================

# BUOC 1: Di toi khu vuc bong
r.forward(1500)       # Tien sang phai
r.turn_left(45)       # Quay cheo len
r.forward(500)

# BUOC 2: Nhat bong
r.grab()

# BUOC 3: Mang den RED Zone
r.turn_left(135)
r.forward(2000)

# BUOC 4: Ghi diem!
r.release()           # +1 diem!
''',
                hints=["Thay doi goc va khoang cach de thu thap nhieu bong hon"],
            ),
            2: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# Robot tai: (1000, 1000)
# Bong tai giua san
# RED Zone tai: (200, 2500)
# ==============================

# BUOC 1: Di den khu vuc co bong
r.forward(___)        # Tien sang phai
r.turn_left(___)      # Quay len
r.forward(500)

# BUOC 2: Nhat bong
r.___()               # Lenh gi de nhat?

# BUOC 3: Quay lai RED Zone
r.turn_left(135)
r.forward(2000)

# BUOC 4: Ghi diem
r.___()               # Lenh gi de tha?
''',
                hints=[
                    "forward(1500) de di 1500mm",
                    "grab() de nhat bong",
                    "release() de tha va ghi diem",
                ],
            ),
            3: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# Robot tai: (1000, 1000) - goc duoi trai
# 10 bong mau tai: (2500-4500, 2500-3000)
# RED Zone tai: (200, 2500) w=1200 h=2000
# SHARED x3 tai: (2800, 2800) w=1400 h=1400 - GAP BA!
# ==============================

# Nhiem vu: Thu thap it nhat 2 bong va ghi diem
# BUOC 1: Di den khu vuc co bong
# BUOC 2: Dung grab() de nhat
# BUOC 3: Di den scoring zone
# BUOC 4: Dung release() de ghi diem
# BUOC 5: Lap lai!
''',
                hints=[
                    "r.forward(distance) de di chuyen",
                    "r.grab() khi o gan bong (300mm)",
                    "r.release() khi trong scoring zone",
                    "Dung vong lap de thu thap nhieu bong",
                ],
            ),
        },
    ),

    Project(
        id="robot_match_strategy",
        title="Chien luoc thi dau",
        title_en="Match Strategy",
        category=CAT_ROBOT,
        category_en=CAT_ROBOT_EN,
        description="Lap trinh chien luoc thi dau day du: quan ly thoi gian, uu tien zone diem cao, phoi hop dong doi.",
        description_en="Program a complete match strategy: time management, prioritize high-score zones, team coordination.",
        concepts=["robot", "strategy", "game theory", "loop", "time management"],
        field_id="eco_equilibrium_2025",
        solution='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm) - 150 giay
# ==============================
# Robot (Ban - RED) tai: (1000, 1000)
# Dong doi: red_1, red_2
# Doi thu: blue_1, blue_2, blue_3
# SHARED x3 tai: (2800, 2800) - GAP BA!
# ==============================

# Chien luoc: Rush SHARED x3 truoc!
r.set_strategy("aggressive")

# BUOC 1: Rush den bong gan SHARED zone
r.forward(2000)       # Tien nhanh sang phai
r.turn_left(30)       # Quay cheo len
r.forward(1000)
r.grab()              # Nhat bong!

# BUOC 2: Ghi diem tai SHARED x3
r.turn_right(60)
r.forward(800)
r.release()           # +3 diem! (1 x 3)

# BUOC 3-6: Thu thap them
for i in range(4):
    r.turn_right(90 * i + 45)
    r.forward(1200)   # Di tim bong
    r.grab()          # Nhat

    r.turn_right(180) # Quay lai
    r.forward(1200)
    r.release()       # Ghi diem!

# Cuoi tran: ve zone an toan
r.turn_left(90)
r.forward(500)
''',
        levels={
            1: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# SHARED x3 tai giua san - GAP BA!
# ==============================

r.set_strategy("aggressive")

# Rush den SHARED x3
r.forward(2000)
r.turn_left(30)
r.forward(1000)
r.grab()              # Nhat bong!
r.turn_right(60)
r.forward(800)
r.release()           # +3 diem!

# Thu thap them - thu thay doi strategy!
for i in range(4):
    r.turn_right(90 * i + 45)
    r.forward(1200)
    r.grab()
    r.turn_right(180)
    r.forward(1200)
    r.release()
''',
                hints=["Thu thay doi strategy va so vong lap"],
            ),
            2: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm)
# ==============================
# SHARED x3 tai: (2800, 2800) - GAP BA!
# ==============================

r.set_strategy(___)   # "aggressive"?

# Rush den SHARED zone
r.forward(2000)
r.turn_left(30)
r.forward(1000)
r.___()               # Nhat bong
r.turn_right(60)
r.forward(800)
r.___()               # Ghi diem!

# Vong lap thu thap them
for i in range(___):
    r.turn_right(90 * i + 45)
    r.forward(___)
    r.___()           # Nhat
    r.turn_right(180)
    r.forward(___)
    r.___()           # Ghi diem
''',
                hints=[
                    '"aggressive" de choi tan cong',
                    "grab() de nhat, release() de ghi diem",
                    "Lap 4 vong, forward(1200) de di tim bong",
                ],
            ),
            3: ProjectLevel(
                code='''\
import robot

r = robot.Robot()

# ==============================
# BAN DO: Eco Equilibrium 2025 (7000x7000mm) - 150 giay
# ==============================
# Robot (Ban - RED) tai: (1000, 1000)
# 10 bong mau tai giua san
# RED Zone tai: (200, 2500) x1 | BLUE Zone tai: (5600, 2500) x1
# SHARED x3 tai: (2800, 2800) - GAP BA!
# ==============================

# Nhiem vu: Lap trinh chien luoc thi dau hoan chinh
# - set_strategy("aggressive" / "defensive" / "cooperative")
# - Uu tien SHARED x3 (gap 3 diem!)
# - Dung vong lap de thu thap nhieu bong
# - 150 giay / tran
''',
                hints=[
                    "r.set_strategy('aggressive') de bat dau",
                    "SHARED x3 cho gap 3 diem!",
                    "Dung for loop de grab/release nhieu lan",
                    "r.match_time() de xem thoi gian con lai",
                ],
            ),
        },
    ),
]
