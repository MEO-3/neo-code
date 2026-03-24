# NEO CODE — Release & In-App Update Guide

## Contents

1. [Release Rules](#1-release-rules)
2. [Creating a GitHub Release](#2-creating-a-github-release)
3. [In-App Update System](#3-in-app-update-system)
4. [How the Updater Works](#4-how-the-updater-works)
5. [Settings](#5-settings)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Release Rules

### Version format

Follow [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH   e.g. 0.4.0
```

| Bump    | When                                                    | Example            |
|---------|---------------------------------------------------------|--------------------|
| PATCH   | Bug fix, no new features                                | 0.3.0 → 0.3.1     |
| MINOR   | New feature, backward compatible                        | 0.3.1 → 0.4.0     |
| MAJOR   | Breaking change (settings format, API, removed feature) | 0.4.0 → 1.0.0     |

### Pre-release checklist

1. **Bump version** in `pyproject.toml`:

   ```toml
   [project]
   version = "0.4.0"
   ```

2. **Test on ARM device** — the target platform is Armbian ARM (2 GB RAM, 16 GB eMMC). Always verify the wheel installs and runs correctly on real hardware before releasing.

3. **Verify `--no-deps` install** — the in-app updater uses `pip install --no-deps` to skip PyQt5 (provided by system `apt` on ARM). Ensure no new runtime dependencies were added without updating the install command.

4. **Run the app** — confirm startup, basic editing, code execution, and that the version shown in Settings matches the new version.

5. **Write release notes** — describe what changed in user-facing language (Vietnamese preferred for end users). Include bug fixes, new features, and any breaking changes.

### Git tag rules

- Tags **must** match the pattern `v{VERSION}` — e.g. `v0.4.0`
- The tag version **must** match `pyproject.toml` `version`
- Tags are created on the `main` branch only — never on feature branches
- Never delete or move a published tag

### Wheel naming

The wheel **must** be a pure-Python wheel (`py3-none-any`). This ensures a single wheel works on both x86 dev machines and ARM target devices:

```
neo_code-0.4.0-py3-none-any.whl
```

---

## 2. Creating a GitHub Release

### Step-by-step

```bash
# 1. Ensure you're on main with a clean working tree
git checkout main
git pull origin main
git status   # must be clean

# 2. Bump version in pyproject.toml (already done in pre-release checklist)

# 3. Commit the version bump
git add pyproject.toml
git commit -m "chore: bump version to 0.4.0"
git push origin main

# 4. Build the wheel
rm -rf dist/
hatch build

# 5. Create and push the tag
git tag v0.4.0
git push origin v0.4.0

# 6. Create the GitHub Release with the wheel attached
gh release create v0.4.0 dist/neo_code-0.4.0-py3-none-any.whl \
  --title "v0.4.0" \
  --notes "Release notes here..."
```

### Release asset rules

- **Exactly one `.whl` file** must be attached to each release. The in-app updater scans the `assets[]` list for the first file ending in `.whl`.
- The `.tar.gz` source distribution is optional — the updater ignores it.
- Do not attach multiple wheels (e.g. for different platforms). NEO Code produces a single `py3-none-any` wheel.

### Release notes format

Write notes in markdown. The in-app update dialog shows these as plain text. Keep them concise:

```markdown
## Có gì mới

- Thêm tính năng cập nhật phần mềm từ trong ứng dụng
- Sửa lỗi không lưu được file khi đường dẫn có dấu cách

## Sửa lỗi

- Sửa lỗi hiển thị trên màn hình nhỏ
```

---

## 3. In-App Update System

### Overview

NEO Code includes a built-in software updater that checks GitHub Releases for newer versions, downloads the wheel, and installs it — all from within the app. This eliminates the need for manual `scp` + `pip install` on ARM devices.

### Architecture

```
core/version.py       — get_version(): reads installed version
core/updater.py       — UpdateChecker(QThread): check + download + install
core/event_bus.py     — update_available signal bridges updater → UI
core/settings.py      — auto_check_update setting
ui/toolbar.py         — "⬆ Cập nhật" indicator button (hidden by default)
ui/update_dialog.py   — modal dialog: release notes + progress + install
ui/settings_dialog.py — settings with version display + manual check button
app.py                — triggers auto-check on startup
```

### User flow

1. **Automatic check** — On startup, if `auto_check_update` is enabled (default: `True`), the app queries the GitHub API in a background thread. If a newer version exists, the toolbar shows a green "⬆ Cập nhật" button.

2. **Manual check** — The user clicks ⚙ (gear icon) in the toolbar to open Settings. The dialog shows the current version and a "Kiểm tra cập nhật" button. Clicking it checks GitHub for updates.

3. **Install flow** — When an update is found (either way), clicking the indicator opens the Update Dialog showing the new version and release notes. The user clicks "Cập nhật" to download and install. A progress bar shows download progress. On success, a "Khởi động lại" (restart) button appears.

---

## 4. How the Updater Works

### Version detection

`core/version.py` → `get_version()`:

1. Tries `importlib.metadata.version("neo-code")` — works when installed from a wheel
2. Falls back to parsing `pyproject.toml` — works for editable installs (`pip install -e .`)
3. Returns `"0.0.0"` if both fail

### GitHub API check

`core/updater.py` → `UpdateChecker._do_check()`:

- **Endpoint:** `GET https://api.github.com/repos/MEO-3/neo-code/releases/latest`
- **Rate limit:** 60 requests/hour per IP (unauthenticated). One check per app launch is well within this limit.
- **Comparison:** Uses `packaging.version.Version` for proper semver comparison. Only emits `update_available` if the remote version is strictly greater.
- **Wheel discovery:** Scans `assets[]` for the first file ending in `.whl`.
- **Failure handling:** Silently returns on any error (no network, rate limited, invalid response). No error is shown to the user.

### Download and install

`core/updater.py` → `UpdateChecker._do_download_and_install()`:

1. Downloads the `.whl` to `/tmp/` using `urllib.request.urlretrieve` with a progress callback
2. Runs `pip install --no-deps --upgrade /tmp/neo_code_X.Y.Z.whl`
3. `--no-deps` is **critical** on ARM: it prevents pip from trying to rebuild PyQt5 from source (PyQt5 is installed via system `apt`)
4. Emits `update_finished(success, message)`

### Thread safety

All network and subprocess I/O runs in a `QThread`. Signals (`update_available`, `download_progress`, `update_finished`) are emitted from the worker thread and delivered to the main thread via Qt's signal/slot mechanism. The UI never blocks.

---

## 5. Settings

### auto_check_update

| Key                 | Type | Default | Location                              |
|---------------------|------|---------|---------------------------------------|
| `auto_check_update` | bool | `True`  | `~/.config/neo-code/settings.json`    |

The user can toggle this in the Settings dialog (⚙ button in toolbar):

- **Checked** — the app checks for updates automatically on every startup
- **Unchecked** — no automatic check; user must check manually via Settings

The setting is persisted immediately when toggled.

### Accessing in code

```python
from neo_code.core.settings import Settings

settings = Settings()
if settings.auto_check_update:
    # start update check
    ...
```

---

## 6. Troubleshooting

### Update check does nothing / no indicator appears

- **No network:** The updater silently fails if the device is offline. Connect to the internet and try the manual check in Settings.
- **Rate limited:** GitHub allows 60 unauthenticated API requests per hour per IP. If multiple devices share an IP (e.g. a classroom), this limit may be hit. Wait an hour.
- **No `.whl` in release:** The updater only looks for `.whl` assets. Ensure the GitHub Release has a wheel attached.
- **Version tag format:** The release `tag_name` must start with `v` followed by a valid semver string (e.g. `v0.4.0`). The `v` prefix is stripped before comparison.

### pip install fails during update

- **Permission denied:** The venv may require `sudo`. If deploying with a system-wide venv, ensure the user has write access.
- **Disk full:** The ARM device has only 16 GB eMMC. Check available space with `df -h`.
- **Dependency conflict:** If `--no-deps` is removed by accident, pip may try to build PyQt5 from source. Always use `--no-deps`.

### Version in Settings shows "0.0.0"

- The app is running from source without `pip install -e .`. Install in editable mode:

  ```bash
  pip install -e .
  ```

### Restart button does nothing on some setups

- The restart uses `os.execv()` to replace the current process. This may not work correctly under certain process managers (e.g. systemd). In that case, manually restart:

  ```bash
  systemctl --user restart neo-code
  ```
