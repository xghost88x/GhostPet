#!/usr/bin/env python3
"""Standalone Windows beta updater.

Build as its own one-file executable. GhostPet copies it to a temporary folder
before launch, permitting both GhostPet.exe and the installed updater itself
to be replaced. No shell invocation, no administrator permission, and no edits
to the household save directory.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import messagebox
import urllib.request
import zipfile

REPO = "xghost88x/GhostPet"
RELEASE_URL = f"https://api.github.com/repos/{REPO}/releases?per_page=25"
CHANNEL_TAG = "windows-beta-v"
ASSET_NAME = "GhostPet-Windows-Testers.zip"
MAX_DOWNLOAD = 500 * 1024 * 1024
MAX_ITEM = 270 * 1024 * 1024
ALLOWED = {
    "GhostPet.exe", "GhostPetUpdater.exe", "VERSION",
    "README-Windows.txt", "Install-Windows.cmd",
}
REQUIRED = {"GhostPet.exe", "GhostPetUpdater.exe", "VERSION"}


def request_bytes(url, maximum):
    request = urllib.request.Request(url, headers={
        "User-Agent": "GhostPet-Windows-Beta-Updater/1.0",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError("The release exceeds the safe download limit.")
    return data


def latest_beta(releases):
    """Don't accidentally install the Linux source or unrelated releases."""
    for release in releases:
        tag = release.get("tag_name", "")
        if release.get("draft") or not tag.startswith(CHANNEL_TAG):
            continue
        asset = next((a for a in release.get("assets", [])
                      if a.get("name") == ASSET_NAME and
                      a.get("state") == "uploaded"), None)
        if asset:
            return release, asset
    return None, None


def unpack_release(data):
    """Whitelisted ZIP extraction; rejects traversal and arbitrary programs."""
    files = {}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            parts = info.filename.replace("\\", "/").split("/")
            if (len(parts) not in (1, 2) or any(
                    p in ("", ".", "..") for p in parts) or
                    (len(parts) == 2 and parts[0] != "GhostPet-Windows")):
                raise ValueError("Unexpected file path inside release ZIP.")
            name = parts[-1]
            if name not in ALLOWED:
                raise ValueError("Unexpected file inside release ZIP: " + name)
            if name in files or info.file_size > MAX_ITEM:
                raise ValueError("Invalid release ZIP file: " + name)
            files[name] = archive.read(info)
    if not REQUIRED.issubset(files):
        raise ValueError("Release is missing a required Windows executable.")
    version = files["VERSION"].decode("utf-8").strip()
    if not version or len(version) > 60:
        raise ValueError("Invalid release VERSION file.")
    return files


def wait_for_game(pid, timeout=25):
    """Wait for the application's actual Win32 process handle, not a guessed sleep."""
    if not pid:
        return
    if sys.platform != "win32":
        return
    import ctypes
    SYNCHRONIZE = 0x00100000
    WAIT_OBJECT_0 = 0
    WAIT_TIMEOUT = 258
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel.WaitForSingleObject.restype = ctypes.c_ulong
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_int
    handle = kernel.OpenProcess(SYNCHRONIZE, False, pid)
    if not handle:
        return  # Already closed, or inaccessible (replacement will fail safely).
    try:
        result = kernel.WaitForSingleObject(handle, int(timeout * 1000))
        if result == WAIT_TIMEOUT:
            raise RuntimeError("Close GhostPet before installing the update.")
        if result != WAIT_OBJECT_0:
            raise RuntimeError("Could not confirm GhostPet had closed.")
    finally:
        kernel.CloseHandle(handle)


def install_files(app_dir, files, progress):
    """Stage and replace known executable files, rolling back on errors."""
    app_dir = Path(app_dir).resolve()
    if not (app_dir / "GhostPet.exe").is_file():
        raise RuntimeError("This is not a GhostPet Windows installation.")
    with tempfile.TemporaryDirectory(prefix="ghostpet-apply-") as work:
        staging = Path(work)
        updated = staging / "new"
        previous = staging / "old"
        updated.mkdir()
        previous.mkdir()
        for name, data in files.items():
            (updated / name).write_bytes(data)
        replaced = []
        created = []
        try:
            for name in sorted(files, key=lambda n: n == "GhostPetUpdater.exe"):
                current = app_dir / name
                if current.exists():
                    shutil.copy2(current, previous / name)
                    replaced.append(name)
                else:
                    created.append(name)
                progress("Installing " + name + "…")
                os.replace(updated / name, current)
        except Exception:
            for name in replaced:
                original = previous / name
                if original.is_file():
                    shutil.copy2(original, app_dir / name)
            for name in created:
                (app_dir / name).unlink(missing_ok=True)
            raise
    # IMPORTANT: no code ever touches %LOCALAPPDATA%\\GhostPet\\state.json.


def perform_update(app_dir, wait_pid, progress):
    app_dir = Path(app_dir).resolve()
    progress("Finding the latest Windows beta on GitHub…")
    releases = json.loads(request_bytes(RELEASE_URL, 2_000_000))
    release, asset = latest_beta(releases)
    if release is None:
        raise RuntimeError(
            "No published Windows tester release yet. Check GitHub Releases.")
    latest = release["tag_name"][len(CHANNEL_TAG):]
    local_version_file = app_dir / "VERSION"
    current = (local_version_file.read_text(encoding="utf-8").strip()
               if local_version_file.exists() else "")
    if latest == current:
        return "Already on the latest Windows beta (" + latest + ").", False
    download_url = asset.get("browser_download_url", "")
    if not download_url.startswith(
            f"https://github.com/{REPO}/releases/download/"):
        raise ValueError("Release download URL did not come from this repository.")
    progress("Downloading the official Windows beta ZIP…")
    data = request_bytes(download_url, MAX_DOWNLOAD)
    expected = asset.get("digest", "")
    if not expected.startswith("sha256:"):
        raise ValueError("Release has no published SHA256 digest; refusing update.")
    if hashlib.sha256(data).hexdigest().lower() != expected[7:].lower():
        raise ValueError("SHA256 mismatch: update was not installed.")
    progress("Validating app files…")
    files = unpack_release(data)
    if files["VERSION"].decode().strip() != latest:
        raise ValueError("Release tag and bundled version do not match.")
    progress("Waiting for the desktop pet to close…")
    wait_for_game(wait_pid)
    progress("Installing Windows beta " + latest + "…")
    install_files(app_dir, files, progress)
    return "Updated to " + latest + ". Your pets and coins are safe!", True


class UpdateWindow(tk.Tk):
    def __init__(self, app_dir, wait_pid):
        super().__init__()
        self.app_dir = Path(app_dir)
        self.wait_pid = wait_pid
        self.result = queue.Queue()
        self.busy = False
        self.title("GhostPet | Windows Update Center")
        self.geometry("460x230")
        self.resizable(False, False)
        self.configure(bg="#f7eedf")
        self.status = tk.StringVar(value="Check for a newer Windows beta. Your pets are safe.")
        tk.Label(self, text="🐭 GhostPet Windows Beta Updates",
                 bg="#f7eedf", fg="#463f34",
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))
        tk.Label(self, textvariable=self.status, wraplength=425,
                 bg="#f7eedf", fg="#463f34",
                 font=("Segoe UI", 10)).pack(expand=True, padx=15)
        controls = tk.Frame(self, bg="#f7eedf")
        controls.pack(pady=12)
        self.action = tk.Button(controls, text="Check & install update",
                                command=self.begin, width=23)
        self.action.pack(side="left", padx=5)
        tk.Button(controls, text="Close", command=self.destroy,
                  width=12).pack(side="left", padx=5)
        self.after(150, self.process_messages)
        # Opening Update from Pocket Care means the user requested a check.
        if wait_pid:
            self.after(250, self.begin)

    def begin(self):
        if self.busy:
            return
        self.busy = True
        self.action.configure(state="disabled")
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        def progress(message):
            self.result.put(("progress", message))
        try:
            message, changed = perform_update(
                self.app_dir, self.wait_pid, progress)
            self.result.put(("success", (message, changed)))
        except Exception as exc:
            self.result.put(("error", str(exc)))

    def process_messages(self):
        try:
            while True:
                kind, payload = self.result.get_nowait()
                if kind == "progress":
                    self.status.set(payload)
                elif kind == "error":
                    self.status.set("Update failed: " + payload)
                    self.busy = False
                    self.action.configure(state="normal")
                elif kind == "success":
                    message, changed = payload
                    self.status.set(message)
                    self.busy = False
                    if changed:
                        self.action.configure(text="Launch GhostPet",
                                              command=self.launch,
                                              state="normal")
                    else:
                        self.action.configure(state="normal")
        except queue.Empty:
            pass
        self.after(150, self.process_messages)

    def launch(self):
        app = self.app_dir / "GhostPet.exe"
        if app.exists():
            subprocess.Popen([str(app)], cwd=str(self.app_dir))
            self.destroy()
        else:
            messagebox.showerror("Cannot launch", "GhostPet.exe was not found.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-dir", type=Path,
                        default=Path(sys.executable).resolve().parent)
    parser.add_argument("--wait-pid", type=int, default=0)
    args = parser.parse_args()
    app = UpdateWindow(args.app_dir, args.wait_pid)
    app.mainloop()


if __name__ == "__main__":
    main()
