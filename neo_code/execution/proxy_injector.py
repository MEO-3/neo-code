"""
proxy_injector — rewrites student code before execution.

Prepends a path injection so `import turtle` loads our proxy instead
of the standard library module. Pure Python, no Qt dependency.
"""

import sys
import tempfile
from pathlib import Path

# Absolute path to our proxy module directory
_PROXY_DIR = Path(__file__).parent.parent / "features" / "turtle_canvas"


def prepare_script(code: str) -> Path:
    """
    Write student code into a temp file with the proxy path prepended.
    Returns the path to the runnable temp file.
    """
    proxy_dir = str(_PROXY_DIR)
    preamble = (
        "import sys as _sys\n"
        f"_sys.path.insert(0, {proxy_dir!r})\n"
    )
    full_source = preamble + code

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    )
    tmp.write(full_source)
    tmp.flush()
    tmp.close()
    return Path(tmp.name)
