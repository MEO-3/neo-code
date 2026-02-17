"""Turtle-specific hints and guidance."""

TURTLE_CONCEPT_HINTS = {
    "square": (
        "To draw a square, you need to:\n"
        "1. Move forward\n"
        "2. Turn 90 degrees\n"
        "3. Repeat 4 times!\n\n"
        "```python\nfor i in range(4):\n    t.forward(100)\n    t.right(90)\n```"
    ),
    "triangle": (
        "A triangle has 3 sides and 3 angles. The exterior angle is 120 degrees.\n\n"
        "```python\nfor i in range(3):\n    t.forward(100)\n    t.right(120)\n```"
    ),
    "circle": (
        "You can draw a circle using `t.circle(radius)`.\n\n"
        "```python\nt.circle(50)  # circle with radius 50\n```"
    ),
    "star": (
        "A 5-pointed star turns 144 degrees at each point.\n\n"
        "```python\nfor i in range(5):\n    t.forward(100)\n    t.right(144)\n```"
    ),
    "spiral": (
        "A spiral increases the distance with each step.\n\n"
        "```python\nfor i in range(100):\n    t.forward(i * 2)\n    t.right(90)\n```"
    ),
    "polygon": (
        "Any regular polygon: turn angle = 360 / number_of_sides.\n\n"
        "```python\nsides = 6  # hexagon\nfor i in range(sides):\n"
        "    t.forward(60)\n    t.right(360 / sides)\n```"
    ),
    "color": (
        "Change colors with `pencolor()` and `fillcolor()`.\n\n"
        "```python\nt.pencolor('red')\nt.fillcolor('yellow')\n"
        "t.begin_fill()\n# draw shape here\nt.end_fill()\n```"
    ),
    "function": (
        "Create reusable shapes with functions!\n\n"
        "```python\ndef draw_square(size):\n    for i in range(4):\n"
        "        t.forward(size)\n        t.right(90)\n\n"
        "draw_square(100)  # big square\ndraw_square(50)   # small square\n```"
    ),
}


def get_turtle_hint(concept: str) -> str | None:
    """Get a turtle-specific hint for the given concept."""
    return TURTLE_CONCEPT_HINTS.get(concept.lower())


def detect_turtle_intent(code: str) -> str | None:
    """Try to detect what turtle shape/concept the student is working on."""
    code_lower = code.lower()

    if "range(4)" in code and ("90" in code or "right" in code_lower):
        return "square"
    if "range(3)" in code and ("120" in code):
        return "triangle"
    if "circle" in code_lower:
        return "circle"
    if "range(5)" in code and "144" in code:
        return "star"
    if "range(" in code and ("i *" in code or "i*" in code):
        return "spiral"
    if "360" in code and "/" in code:
        return "polygon"
    if "pencolor" in code_lower or "fillcolor" in code_lower:
        return "color"
    if "def " in code and ("forward" in code_lower or "right" in code_lower):
        return "function"

    return None
