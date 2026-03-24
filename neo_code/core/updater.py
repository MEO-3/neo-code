"""
UpdateChecker — QThread that checks GitHub Releases for newer versions,
downloads the wheel, and installs it via pip.

All network I/O runs off the main thread so the UI stays responsive.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal

from neo_code.core.version import get_version

_API_URL = "https://api.github.com/repos/MEO-3/neo-code/releases/latest"


class UpdateChecker(QThread):
    """Background thread for checking and applying updates."""

    update_available = pyqtSignal(str, str, str)   # (new_version, release_notes, download_url)
    download_progress = pyqtSignal(int)             # percentage 0-100
    update_finished = pyqtSignal(bool, str)         # (success, message)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._download_url: str | None = None

    # ── Public API ─────────────────────────────────────────────────────────

    def check(self) -> None:
        """Start the check in this thread."""
        self._download_url = None
        self.start()

    def download_and_install(self, url: str) -> None:
        """Download the wheel at *url* and install it (call from main thread)."""
        self._download_url = url
        self.start()

    # ── Thread entry point ─────────────────────────────────────────────────

    def run(self) -> None:  # noqa: D401
        if self._download_url:
            self._do_download_and_install(self._download_url)
        else:
            self._do_check()

    # ── Internals ──────────────────────────────────────────────────────────

    def _do_check(self) -> None:
        try:
            req = urllib.request.Request(
                _API_URL,
                headers={"Accept": "application/vnd.github+json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return  # silently fail — offline or rate-limited

        tag = data.get("tag_name", "")
        new_version = tag.lstrip("v")
        if not new_version:
            return

        try:
            from packaging.version import Version
            if Version(new_version) <= Version(get_version()):
                return
        except Exception:
            return

        # Find .whl asset
        whl_url: str | None = None
        for asset in data.get("assets", []):
            name: str = asset.get("name", "")
            if name.endswith(".whl"):
                whl_url = asset.get("browser_download_url")
                break

        if not whl_url:
            return

        notes = data.get("body", "") or ""
        self.update_available.emit(new_version, notes, whl_url)

    def _do_download_and_install(self, url: str) -> None:
        tmp_dir = Path(tempfile.gettempdir())
        filename = url.rsplit("/", 1)[-1]
        dest = tmp_dir / filename

        # Download with progress
        try:
            def _reporthook(block_num: int, block_size: int, total_size: int) -> None:
                if total_size > 0:
                    pct = min(int(block_num * block_size * 100 / total_size), 100)
                    self.download_progress.emit(pct)

            urllib.request.urlretrieve(url, str(dest), reporthook=_reporthook)
            self.download_progress.emit(100)
        except Exception as exc:
            self.update_finished.emit(False, f"Lỗi tải xuống: {exc}")
            return

        # Install
        try:
            result = subprocess.run(
                [
                    "pip", "install",
                    "--no-deps",
                    "--upgrade",
                    str(dest),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                self.update_finished.emit(True, "Cập nhật thành công! Khởi động lại để áp dụng.")
            else:
                self.update_finished.emit(False, f"pip install thất bại:\n{result.stderr}")
        except Exception as exc:
            self.update_finished.emit(False, f"Lỗi cài đặt: {exc}")
