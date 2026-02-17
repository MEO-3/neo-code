"""Curriculum and lesson definitions."""

from dataclasses import dataclass, field


@dataclass
class Exercise:
    """A single exercise."""
    id: str
    title: str
    description: str
    starter_code: str
    expected_concepts: list[str] = field(default_factory=list)
    difficulty: int = 1  # 1-5


@dataclass
class Lesson:
    """A lesson containing exercises."""
    id: int
    title: str
    description: str
    exercises: list[Exercise] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)


# Phase 1 Curriculum: Python & Turtle
PHASE1_LESSONS = [
    Lesson(
        id=1,
        title="First Steps with Python",
        description="Learn to print, use variables, and basic math",
        concepts=["print", "variables", "math", "strings"],
        exercises=[
            Exercise(
                id="p1_l1_e1",
                title="Hello World",
                description="Print your name using the print() function",
                starter_code='# Print your name!\nprint("Hello, my name is ___")\n',
                expected_concepts=["print"],
                difficulty=1,
            ),
            Exercise(
                id="p1_l1_e2",
                title="Calculator",
                description="Use Python as a calculator to solve math problems",
                starter_code='# Calculate: 15 + 27\nresult = ___\nprint("The answer is:", result)\n',
                expected_concepts=["variables", "math"],
                difficulty=1,
            ),
        ],
    ),
    Lesson(
        id=2,
        title="Drawing with Turtle",
        description="Create your first drawings with Turtle graphics",
        concepts=["turtle", "forward", "left", "right"],
        exercises=[
            Exercise(
                id="p1_l2_e1",
                title="Draw a Line",
                description="Use forward() to draw a straight line",
                starter_code='import turtle\nt = turtle.Turtle()\n\n# Draw a line 200 pixels long\nt.forward(___)\n\nturtle.done()\n',
                expected_concepts=["turtle", "forward"],
                difficulty=1,
            ),
            Exercise(
                id="p1_l2_e2",
                title="Draw a Square",
                description="Draw a square using forward() and right()",
                starter_code='import turtle\nt = turtle.Turtle()\n\n# Draw a square with side length 100\n# Hint: a square has 4 sides and 90 degree angles\n\nturtle.done()\n',
                expected_concepts=["turtle", "forward", "right", "loop"],
                difficulty=2,
            ),
        ],
    ),
    Lesson(
        id=3,
        title="Loops and Patterns",
        description="Use for loops to create amazing patterns",
        concepts=["for loop", "range", "patterns"],
        exercises=[
            Exercise(
                id="p1_l3_e1",
                title="Colorful Star",
                description="Draw a 5-pointed star with different colors",
                starter_code='import turtle\nt = turtle.Turtle()\ncolors = ["red", "blue", "green", "yellow", "purple"]\n\n# Draw a star with 5 points\n# Each point turns 144 degrees\n\nturtle.done()\n',
                expected_concepts=["for loop", "color", "turtle"],
                difficulty=2,
            ),
            Exercise(
                id="p1_l3_e2",
                title="Spiral Pattern",
                description="Create a beautiful spiral using increasing distances",
                starter_code='import turtle\nt = turtle.Turtle()\nt.speed(0)\n\n# Draw a spiral\n# Hint: increase the distance each time\nfor i in range(100):\n    t.forward(___)\n    t.right(___)\n\nturtle.done()\n',
                expected_concepts=["for loop", "math", "turtle"],
                difficulty=3,
            ),
        ],
    ),
    Lesson(
        id=4,
        title="Functions - Reusable Shapes",
        description="Create your own functions to draw shapes",
        concepts=["function", "def", "parameters"],
        exercises=[
            Exercise(
                id="p1_l4_e1",
                title="Shape Function",
                description="Create a function that draws any regular polygon",
                starter_code='import turtle\nt = turtle.Turtle()\n\ndef draw_polygon(sides, size):\n    # Draw a polygon with the given number of sides\n    # Turn angle = 360 / sides\n    pass\n\n# Test: draw a hexagon\ndraw_polygon(6, 60)\n\nturtle.done()\n',
                expected_concepts=["function", "parameters", "loop"],
                difficulty=3,
            ),
        ],
    ),
]


def get_lessons(phase: int) -> list[Lesson]:
    """Get lessons for the given phase."""
    if phase == 1:
        return PHASE1_LESSONS
    return []


def get_exercise(exercise_id: str) -> Exercise | None:
    """Find an exercise by ID."""
    for lesson in PHASE1_LESSONS:
        for exercise in lesson.exercises:
            if exercise.id == exercise_id:
                return exercise
    return None
