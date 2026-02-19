"""Code completion using Jedi library."""
from __future__ import annotations


from typing import Optional


def get_completions(code: str, line: int, column: int) -> list[dict]:
    """Get autocompletion suggestions at the given position.


    Returns list of dicts with keys: name, type, description.
    """
    try:
        import jedi
        script = jedi.Script(code)
        completions = script.complete(line, column)
        return [
            {
                "name": c.name,
                "type": c.type,
                "description": c.description,
            }
            for c in completions[:20]  # Limit results
        ]
    except ImportError:
        return []
    except Exception:
        return []


def get_help(code: str, line: int, column: int) -> Optional[str]:
    """Get help/documentation for the symbol at the given position."""
    try:
        import jedi
        script = jedi.Script(code)
        names = script.help(line, column)
        if names:
            docstrings = [n.docstring() for n in names if n.docstring()]
            if docstrings:
                return docstrings[0]
    except (ImportError, Exception):
        pass
    return None
