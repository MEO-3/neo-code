"""Rule-based hint database for common beginner errors (fallback when LLM unavailable)."""
from __future__ import annotations


import re


# Map of error patterns to helpful hints
ERROR_HINTS: list[tuple[str, str]] = [
    # Syntax errors
    (
        r"(?i)expected ':'",
        "You're missing a colon `:` at the end of the line. "
        "Remember: `if`, `for`, `while`, `def`, and `class` statements need a `:` at the end.\n\n"
        "Example: `for i in range(4):`"
    ),
    (
        r"(?i)unexpected indent",
        "There's extra spaces at the beginning of this line. "
        "Make sure your indentation matches the code block it belongs to. "
        "Use exactly 4 spaces for each level."
    ),
    (
        r"(?i)expected an indented block",
        "After a line ending with `:`, you need to add indented code (4 spaces). "
        "For example:\n\n```python\nfor i in range(4):\n    print(i)  # This line is indented\n```"
    ),
    (
        r"(?i)EOL while scanning string",
        "You forgot to close your string! Make sure every opening quote `'` or `\"` has "
        "a matching closing quote."
    ),
    (
        r"(?i)unexpected EOF",
        "Something is not closed properly. Check that every `(` has a `)`, "
        "every `[` has a `]`, and every `{` has a `}`."
    ),
    (
        r"(?i)invalid syntax",
        "There's a syntax error - something Python doesn't understand. "
        "Check for typos, missing commas, or unclosed brackets near this line."
    ),
    (
        r"(?i)SyntaxError",
        "There's a syntax error in your code. Look at the line number and check "
        "for typos, missing colons, or unclosed brackets."
    ),

    # Name errors
    (
        r"(?i)name '(\w+)' is not defined",
        "Python doesn't recognize the name `{match}`. "
        "This usually means:\n"
        "- You haven't defined this variable yet\n"
        "- You made a typo in the variable name\n"
        "- You forgot to `import` a module"
    ),
    (
        r"(?i)undefined name '(\w+)'",
        "The name `{match}` hasn't been defined. "
        "Make sure you've created this variable or imported this module before using it."
    ),

    # Type errors
    (
        r"(?i)TypeError.*can't multiply",
        "You're trying to multiply two types that don't work together. "
        "Make sure you're using numbers for math operations. "
        "Use `int()` or `float()` to convert strings to numbers."
    ),
    (
        r"(?i)TypeError.*unsupported operand",
        "You're using an operator (+, -, *, /) with the wrong types. "
        "For example, you can't add a string and a number directly. "
        "Use `str()` or `int()` to convert types."
    ),
    (
        r"(?i)TypeError.*'(\w+)' object is not callable",
        "You're trying to call `{match}` like a function (with parentheses), "
        "but it's not a function. Remove the `()` if it's a variable."
    ),

    # Index errors
    (
        r"(?i)IndexError.*list index out of range",
        "You're trying to access a list position that doesn't exist. "
        "Remember: Python lists start at index 0. "
        "A list with 3 items has indices 0, 1, 2 (not 3!)."
    ),

    # Import errors
    (
        r"(?i)ModuleNotFoundError.*No module named '(\w+)'",
        "Python can't find the module `{match}`. "
        "Make sure:\n"
        "- You spelled the module name correctly\n"
        "- The module is installed (try: `pip install {match}`)"
    ),

    # Value errors
    (
        r"(?i)ValueError.*invalid literal for int",
        "You're trying to convert something to a number, but it's not a valid number. "
        "Make sure the value contains only digits before converting with `int()`."
    ),

    # Indentation
    (
        r"(?i)IndentationError",
        "Your code indentation is inconsistent. In Python, indentation matters! "
        "Use exactly 4 spaces for each level. Don't mix tabs and spaces."
    ),

    # Division by zero
    (
        r"(?i)ZeroDivisionError",
        "You're dividing by zero, which is mathematically impossible! "
        "Check your division operation and make sure the denominator is not 0."
    ),

    # Turtle-specific
    (
        r"(?i)turtle.*has no attribute",
        "You're calling a turtle method that doesn't exist. "
        "Common turtle methods: `forward()`, `backward()`, `left()`, `right()`, "
        "`penup()`, `pendown()`, `pencolor()`, `circle()`."
    ),

    # Timeout
    (
        r"(?i)timeout|timed out",
        "Your code took too long to run! This usually means you have an **infinite loop**. "
        "Check your `while` loops - make sure the condition will eventually become `False`."
    ),
]


def get_rule_based_hint(error_text: str) -> str | None:
    """Get a hint for the given error text using pattern matching.


    Returns a helpful hint string, or None if no matching pattern is found.
    """
    for pattern, hint_template in ERROR_HINTS:
        match = re.search(pattern, error_text)
        if match:
            # Replace {match} with the first capture group if available
            if match.groups():
                return hint_template.replace("{match}", match.group(1))
            return hint_template

    return None
