#!/usr/bin/env bash
# Per-user Zorin/GNOME installer. No sudo and no changes to saved pets.
set -euo pipefail
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
destination="$HOME/Applications/GhostPet"

python3 - "$source_dir" "$destination" <<'PY'
import os
import shutil
import subprocess
import sys
from pathlib import Path

source, destination = map(lambda p: Path(p).resolve(), sys.argv[1:3])
files = (
    "ghostpet.py", "activities.py", "house.py", "nursery.py",
    "updater.py", "updater_core.py", "start.sh", "update.sh",
    "install.sh", "requirements.txt", "VERSION",
    "README.md", "CHANGELOG.md", "LICENSE", "CONTRIBUTING.md",
    "assets/ghostpet.svg",
)
destination.mkdir(parents=True, exist_ok=True)
for relative in files:
    src = source / relative
    dst = destination / relative
    if not src.is_file():
        if relative in ("LICENSE", "CONTRIBUTING.md"):
            continue
        raise SystemExit(f"Installation stopped: {relative} is missing.")
    if src == dst:
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

for name in ("start.sh", "update.sh", "install.sh"):
    (destination / name).chmod(0o755)

icon_dir = Path.home() / ".local/share/icons/hicolor/scalable/apps"
icon_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(destination / "assets/ghostpet.svg", icon_dir / "ghostpet.svg")

app_dir = Path.home() / ".local/share/applications"
app_dir.mkdir(parents=True, exist_ok=True)

def quote(path):
    return '"' + str(path).replace('\\', '\\\\').replace('"', '\\"') + '"'

def desktop_entry(name, command, comment, updater_action=False):
    parts = [
        "[Desktop Entry]", "Version=1.0", "Type=Application", f"Name={name}",
        f"Comment={comment}", f"Exec={quote(command)}", "Icon=ghostpet",
        "Terminal=false", "StartupNotify=true", "Categories=Game;Utility;",
    ]
    if updater_action:
        parts.append("Actions=Update;")
        parts += ["", "[Desktop Action Update]", "Name=Update Ghost Pet",
                  f"Exec={quote(destination / 'update.sh')}"]
    return "\n".join(parts) + "\n"

main_entry = desktop_entry("Ghost Pet", destination / "start.sh",
                           "Your cozy little desktop companion", True)
updater_entry = desktop_entry("Update Ghost Pet", destination / "update.sh",
                              "Check for Ghost Pet updates")
(app_dir / "org.ghostpet.GhostPet.desktop").write_text(main_entry, encoding="utf-8")
(app_dir / "org.ghostpet.Updater.desktop").write_text(updater_entry, encoding="utf-8")

desktop = Path.home() / "Desktop"
try:
    found = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True,
                           text=True, timeout=4)
    if found.returncode == 0 and found.stdout.strip():
        desktop = Path(found.stdout.strip())
except (FileNotFoundError, subprocess.TimeoutExpired):
    pass
if desktop.is_dir():
    shortcut = desktop / "Ghost Pet.desktop"
    shortcut.write_text(main_entry, encoding="utf-8")
    shortcut.chmod(0o755)
    try:
        subprocess.run(["gio", "set", str(shortcut), "metadata::trusted", "true"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=4, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print(f"Desktop shortcut: {shortcut}")
print(f"Installed at: {destination}")
print("Open your application menu and search for 'Ghost Pet'.")
print("You can also search for 'Update Ghost Pet' to install future updates.")
print("Your pet's saved data in ~/.local/share/ghostpet was not touched.")
PY
