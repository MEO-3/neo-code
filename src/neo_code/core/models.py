"""Data models for NEO CODE."""
from __future__ import annotations


from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class ErrorSeverity(Enum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    HINT = auto()


class CodePattern(Enum):
    """Detected code patterns for AI context."""

    TURTLE_DRAWING = auto()
    LOOP_CONSTRUCT = auto()
    FUNCTION_DEFINITION = auto()
    VARIABLE_ASSIGNMENT = auto()
    CONDITIONAL = auto()
    LIST_USAGE = auto()
    GPIO_SETUP = auto()
    SENSOR_READ = auto()
    ACTUATOR_CONTROL = auto()
    IMPORT_STATEMENT = auto()
    CLASS_DEFINITION = auto()
    STRING_FORMATTING = auto()
    ERROR_HANDLING = auto()
    ROBOT_PROGRAMMING = auto()


@dataclass
class CodeError:
    """A single code error or warning."""
    line: int
    column: int
    message: str
    severity: ErrorSeverity
    error_code: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class AnalysisResult:
    """Output of the CodeAnalyzer."""
    code_hash: str
    errors: list[CodeError] = field(default_factory=list)
    warnings: list[CodeError] = field(default_factory=list)
    patterns: list[CodePattern] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    defined_functions: list[str] = field(default_factory=list)
    defined_variables: list[str] = field(default_factory=list)
    line_count: int = 0
    is_syntactically_valid: bool = True
    complexity_score: int = 0


class DrawCommandType(Enum):
    """Turtle drawing command types."""
    FORWARD = auto()
    BACKWARD = auto()
    LEFT = auto()
    RIGHT = auto()
    PENUP = auto()
    PENDOWN = auto()
    PENCOLOR = auto()
    PENSIZE = auto()
    FILLCOLOR = auto()
    BEGIN_FILL = auto()
    END_FILL = auto()
    GOTO = auto()
    CIRCLE = auto()
    DOT = auto()
    CLEAR = auto()
    RESET = auto()
    SPEED = auto()
    STAMP = auto()
    HIDETURTLE = auto()
    SHOWTURTLE = auto()


@dataclass
class DrawCommand:
    """A single turtle drawing command for the canvas."""
    command_type: DrawCommandType
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of executing student code."""
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float
    was_timeout: bool = False
    was_killed: bool = False
    draw_commands: list[DrawCommand] = field(default_factory=list)


class HintLevel(Enum):
    """Progressive hint levels for pedagogical approach."""
    NUDGE = auto()       # "Think about what happens when..."
    GUIDANCE = auto()    # "The issue is related to your loop variable"
    EXPLICIT = auto()    # "Change line 5: use range(4) instead of range(3)"
    SOLUTION = auto()    # Full corrected code


@dataclass
class AIResponse:
    """Structured response from the AI assistant."""
    message: str
    hint_level: HintLevel
    related_lines: list[int] = field(default_factory=list)
    code_suggestion: Optional[str] = None
    concept_name: Optional[str] = None
    is_encouragement: bool = False
    is_error_explanation: bool = False


@dataclass
class StudentProfile:
    """Student learning profile and progress."""
    student_id: str
    name: str = ""
    current_phase: int = 1
    current_lesson: int = 1
    skill_level: int = 1
    level: int = 1  # Difficulty level: 1=Explorer, 2=Programmer, 3=Expert
    exercises_completed: list[str] = field(default_factory=list)
    common_error_patterns: dict[str, int] = field(default_factory=dict)
    total_code_runs: int = 0
    total_errors_fixed: int = 0
