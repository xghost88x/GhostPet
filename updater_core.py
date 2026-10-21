"""Safe, user-requested Ghost Pet source updates from the public GitHub repo.

The companion save is kept separately at ~/.local/share/ghostpet/state.json.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import time
import urllib.request
import zipfile

REPO = "xghost88x/GhostPet"
API_URL = f"https://api.github.com/repos/{REPO}/commits/main"
MAX_ARCHIVE_SIZE = 32 * 1024 * 1024
MAX_SINGLE_FILE = 8 * 1024 * 1024
FILES = (
    "ghostpet.py", "house.py", "activities.py", "nursery.py",
    "pet_presence.py", "adopted_sprites.py", "cottage_art.py",
    "updater.py", "updater_core.py", "start.sh", "update.sh",
    "install.sh", "requirements.txt", "VERSION", "README.md",
    "CHANGELOG.md", "LICENSE", "CONTRIBUTING.md",
    "assets/ghostpet.svg",
)
REQUIRED = {
    "ghostpet.py", "house.py", "activities.py", "nursery.py",
    "pet_presence.py", "adopted_sprites.py", "cottage_art.py",
    "updater.py", "updater_core.py", "start.sh", "update.sh",
    "install.sh", "requirements.txt", "VERSION", "assets/ghostpet.svg",
}


def request_bytes(url, limit):
    req = urllib.request.Request(
        url, headers={"User-Agent": "GhostPet-Updater/0.5 (Linux; public GitHub)"}
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("The update exceeds its allowed download size.")
    return data


def latest_revision():
    result = json.loads(request_bytes(API_URL, 2_000_000).decode("utf-8"))
    sha = result.get("sha", "")
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("GitHub did not return a valid source revision.")
    return sha


def archive_files(data):
    """Validate archive and return only the app files we explicitly maintain.

    Never extract blindly: reject traversal paths, symlinks and oversized files.
    """
    found = {}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for item in archive.infolist():
            name = PurePosixPath(item.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("Unsafe update archive path.")
            if item.is_dir():
                continue
            if stat.S_ISLNK((item.external_attr >> 16) & 0xFFFF):
                raise ValueError("Unsafe symbolic link in the update archive.")
            if len(name.parts) < 2:
                raise ValueError("Unexpected update archive structure.")
            relative = "/".join(name.parts[1:])
            if relative not in FILES:
                continue
            if item.file_size > MAX_SINGLE_FILE:
                raise ValueError(f"Update file is too large: {relative}")
            found[relative] = archive.read(item)
    missing = REQUIRED - set(found)
    if missing:
        raise ValueError("Update missing required files: " + ", ".join(sorted(missing)))
    return found


def other_running_instance(app_dir, exclude_pid=None):
    """Recognize Ghost Pet processes in this installation, not generic Python."""
    proc = Path("/proc")
    if not proc.is_dir():
        return False
    script = str((app_dir / "ghostpet.py").resolve()).encode("utf-8")
    for candidate in proc.iterdir():
        if not candidate.name.isdigit() or int(candidate.name) in (os.getpid(), exclude_pid):
            continue
        try:
            cmdline = (candidate / "cmdline").read_bytes().split(b"\0")
            if script in cmdline:
                return True
        except (OSError, PermissionError):
            continue
    return False


def wait_for_process(pid, progress):
    if not pid:
        return
    for _ in range(200):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        except PermissionError:
            return
        time.sleep(.1)
    raise RuntimeError("Ghost Pet has not closed. Please quit it and retry.")


def update_app(app_dir, progress=lambda message: None, wait_pid=None):
    app_dir = Path(app_dir).resolve()
    if not app_dir.is_dir() or not (app_dir / "start.sh").exists():
        raise RuntimeError("Install Ghost Pet with install.sh before updating.")
    progress("Waiting for Ghost Pet to close…")
    wait_for_process(wait_pid, progress)
    if other_running_instance(app_dir):
        raise RuntimeError("Close the running Ghost Pet before installing an update.")

    progress("Checking the latest GitHub revision…")
    newest = latest_revision()
    revision_file = app_dir / ".ghostpet-revision"
    installed = revision_file.read_text(encoding="ascii").strip() if revision_file.exists() else ""
    if newest == installed and all((app_dir / file).is_file() for file in REQUIRED):
        return "You're already on the latest Ghost Pet version!", False

    progress("Downloading the new version securely…")
    url = f"https://codeload.github.com/{REPO}/zip/{newest}"
    payload = request_bytes(url, MAX_ARCHIVE_SIZE)
    files = archive_files(payload)

    # Back up the pet save before any app files are replaced.
    state = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "ghostpet/state.json"
    if state.is_file():
        backup_dir = state.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(state, backup_dir / f"state-before-update-{time.strftime('%Y%m%d-%H%M%S')}.json")

    progress("Backing up previous app files…")
    with tempfile.TemporaryDirectory(prefix=".ghostpet-stage-", dir=app_dir) as temp:
        staged = Path(temp)
        old = staged / "old"
        old.mkdir()
        fresh = staged / "new"
        fresh.mkdir()
        created = []
        for rel, data in files.items():
            dest = fresh / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            target = app_dir / rel
            if target.is_file():
                previous = old / rel
                previous.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, previous)
            else:
                created.append(rel)
        if revision_file.is_file():
            shutil.copy2(revision_file, old / ".ghostpet-revision")

        progress("Installing update (pet data is untouched)…")
        try:
            for rel in files:
                target = app_dir / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(fresh / rel, target)
                if rel.endswith(".sh"):
                    target.chmod(0o755)
            revision_file.write_text(newest + "\n", encoding="ascii")
        except Exception:
            # Restore old files and remove newly created files on partial failure.
            for rel in files:
                target = app_dir / rel
                original = old / rel
                if original.is_file():
                    shutil.copy2(original, target)
                elif rel in created:
                    target.unlink(missing_ok=True)
            if (old / ".ghostpet-revision").is_file():
                shutil.copy2(old / ".ghostpet-revision", revision_file)
            else:
                revision_file.unlink(missing_ok=True)
            raise

        # Retain one rollback snapshot, excluding all user data and .venv.
        previous_version = app_dir / ".previous-version"
        previous_tmp = app_dir / ".previous-version-new"
        if previous_tmp.exists():
            shutil.rmtree(previous_tmp)
        shutil.copytree(old, previous_tmp)
        if previous_version.exists():
            shutil.rmtree(previous_version)
        previous_tmp.rename(previous_version)

    # Refresh icon in the user's app menu too.
    icon_target = Path.home() / ".local/share/icons/hicolor/scalable/apps/ghostpet.svg"
    try:
        icon_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(app_dir / "assets/ghostpet.svg", icon_target)
    except OSError:
        pass  # App update succeeded; an icon-cache failure is cosmetic.
    version = (app_dir / "VERSION").read_text(encoding="utf-8").strip()
    return f"Updated successfully to {version}. Your pets and coins are safe!", True
