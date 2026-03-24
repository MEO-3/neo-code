"""
Version accessor — reads the installed package version.

Uses importlib.metadata when installed as a wheel; falls back to
parsing pyproject.toml when running from an editable install or source.
"""

from __future__ import annotations


def get_version() -> str:
    """Return the current neo-code version string (e.g. '0.3.0')."""
    try:
        from importlib.metadata import version
        return version("neo-code")
    except Exception:
        pass

    # Fallback: parse pyproject.toml (editable / source installs)
    try:
        from pathlib import Path
        import re

        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
        m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        if m:
            return m.group(1)
    except Exception:
        pass

    return "0.0.0"
