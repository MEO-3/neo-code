"""Parse LLM output into structured AIResponse objects."""

import re

from neo_code.core.models import AIResponse, HintLevel


def parse_response(
    raw_text: str,
    hint_level: HintLevel = HintLevel.GUIDANCE,
    is_error: bool = False,
    is_encouragement: bool = False,
) -> AIResponse:
    """Parse raw LLM text into a structured AIResponse."""
    # Extract code suggestions
    code_suggestion = _extract_code_block(raw_text)

    # Extract referenced line numbers
    related_lines = _extract_line_references(raw_text)

    # Extract concept name if mentioned
    concept_name = _extract_concept(raw_text)

    # Clean the message (remove code blocks that will be shown separately)
    message = raw_text.strip()

    return AIResponse(
        message=message,
        hint_level=hint_level,
        related_lines=related_lines,
        code_suggestion=code_suggestion,
        concept_name=concept_name,
        is_encouragement=is_encouragement,
        is_error_explanation=is_error,
    )


def _extract_code_block(text: str) -> str | None:
    """Extract the first Python code block from the text."""
    pattern = r'```python\s*\n(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _extract_line_references(text: str) -> list[int]:
    """Extract line number references from the text."""
    # Match patterns like "line 5", "Line 10", "dòng 3"
    pattern = r'(?:line|Line|dòng|dong)\s+(\d+)'
    matches = re.findall(pattern, text)
    return [int(m) for m in matches]


def _extract_concept(text: str) -> str | None:
    """Extract the main programming concept being discussed."""
    concepts = {
        "for loop": ["for loop", "vòng lặp for"],
        "while loop": ["while loop", "vòng lặp while"],
        "function": ["function", "hàm", "def"],
        "variable": ["variable", "biến"],
        "if/else": ["if statement", "điều kiện", "if/else"],
        "list": ["list", "danh sách", "mảng"],
        "string": ["string", "chuỗi"],
        "turtle.forward": ["forward", "tiến"],
        "turtle.left": ["left", "trái", "quay"],
        "turtle.right": ["right", "phải"],
        "turtle.circle": ["circle", "hình tròn"],
        "indentation": ["indent", "thụt lề", "indentation"],
        "syntax": ["syntax", "cú pháp"],
        "import": ["import", "thư viện"],
    }

    text_lower = text.lower()
    for concept, keywords in concepts.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return concept

    return None
