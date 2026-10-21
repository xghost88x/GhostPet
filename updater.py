#!/usr/bin/env python3
"""Ghost Pet update window with cancellable, timed, out-of-process downloads.

The update runs in a separate Python subprocess. Qt remains responsive and the
download can be stopped without terminating a worker QThread mid-cleanup.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import time

from PySide6.QtCore import QProcess, QTimer
from PySide6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
)

# Launched with the same Python virtual environment and working directory.
# Kept inline so people updating older copies do not need an extra script.
WORKER_SCRIPT = """
import sys
from pathlib import Path
from updater_core import update_app

def progress(message):
    print("PROGRESS:" + str(message), flush=True)

try:
    text, changed = update_app(
        Path(sys.argv[1]), progress, int(sys.argv[2]) or None)
    print("RESULT:" + ("1:" if changed else "0:") + text, flush=True)
except Exception as exc:
    print("ERROR:" + str(exc), flush=True)
    sys.exit(2)
"""


class UpdaterDialog(QDialog):
    def __init__(self, wait_pid=None):
        super().__init__()
        self.root = Path(__file__).resolve().parent
        self.wait_pid = wait_pid
        self.changed = False
        self.process = None
        self.pending_output = ""
        self.result_message = None
        self.error_message = None
        self.progress_message = "Waiting for updater to start"
        self.started_at = 0.0
        self.timed_out = False
        self.setWindowTitle("Ghost Pet • Update Center")
        self.setMinimumWidth(430)
        self.setStyleSheet("""
            QDialog { background: #f7eedf; color: #494238; }
            QLabel { color: #494238; font-size: 14px; }
            QPushButton { background: #769b80; color: white;
              border-radius: 8px; padding: 11px; font-weight: bold; }
            QPushButton:hover { background: #5c7e67; }
            QPushButton:disabled { background: #adb7a9; }
        """)
        layout = QVBoxLayout(self)
        heading = QLabel("🐭  Ghost Pet Update Center")
        heading.setStyleSheet("font-size: 21px; font-weight: bold;")
        layout.addWidget(heading)
        version_path = self.root / "VERSION"
        version = (version_path.read_text(encoding="utf-8").strip()
                   if version_path.exists() else "unknown")
        layout.addWidget(QLabel("Installed version: " + version))
        self.status = QLabel(
            "Check GitHub for updates. Your saved pets and coins are preserved.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        controls = QHBoxLayout()
        self.action = QPushButton("↻ Check and install updates")
        self.action.clicked.connect(self.action_clicked)
        controls.addWidget(self.action)
        self.cancel = QPushButton("Cancel")
        self.cancel.clicked.connect(self.cancel_download)
        self.cancel.hide()
        controls.addWidget(self.cancel)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        controls.addWidget(self.close_button)
        layout.addLayout(controls)
        self.heartbeat = QTimer(self)
        self.heartbeat.setInterval(1000)
        self.heartbeat.timeout.connect(self.show_progress)
        if wait_pid:
            QTimer.singleShot(150, self.start_update)

    def action_clicked(self):
        if self.changed:
            try:
                subprocess.Popen(
                    [str(self.root / "start.sh")], cwd=str(self.root),
                    start_new_session=True,
                )
            except OSError as exc:
                self.status.setText(f"Could not reopen Ghost Pet: {exc}")
                return
            self.close()
        else:
            self.start_update()

    def start_update(self):
        if self.process is not None and self.process.state() != QProcess.ProcessState.NotRunning:
            return
        self.changed = False
        self.timed_out = False
        self.pending_output = ""
        self.result_message = None
        self.error_message = None
        self.progress_message = "Starting update check…"
        self.started_at = time.monotonic()
        self.action.setEnabled(False)
        self.close_button.setEnabled(False)
        self.cancel.show()
        self.cancel.setEnabled(True)
        self.status.setText(self.progress_message)
        proc = QProcess(self)
        proc.setWorkingDirectory(str(self.root))
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        proc.readyReadStandardOutput.connect(self.read_messages)
        proc.finished.connect(self.update_finished)
        proc.errorOccurred.connect(self.process_error)
        self.process = proc
        self.heartbeat.start()
        proc.start(sys.executable, [
            "-u", "-c", WORKER_SCRIPT, str(self.root), str(self.wait_pid or 0),
        ])

    def read_messages(self):
        if not self.process:
            return
        chunk = bytes(self.process.readAllStandardOutput()).decode("utf-8", "replace")
        self.pending_output += chunk
        while "\n" in self.pending_output:
            line, self.pending_output = self.pending_output.split("\n", 1)
            if line.startswith("PROGRESS:"):
                self.progress_message = line[9:].strip()
                if "Installing update" in self.progress_message:
                    # Never terminate the subprocess during file replacement.
                    self.cancel.setEnabled(False)
            elif line.startswith("RESULT:"):
                self.result_message = line[7:].strip()
            elif line.startswith("ERROR:"):
                self.error_message = line[6:].strip()
            else:
                # Unexpected output is shown as a diagnostic, not swallowed.
                self.progress_message = line.strip() or self.progress_message
        self.show_progress()

    def show_progress(self):
        if not self.process:
            return
        elapsed = int(time.monotonic() - self.started_at)
        self.status.setText(f"{self.progress_message}\nElapsed: {elapsed} seconds")
        # This only stops network/waiting stages. Once files are being backed up
        # or replaced, let the update finish or roll back normally.
        in_install = any(tag in self.progress_message for tag in
                         ("Backing up", "Installing update"))
        if elapsed >= 95 and not in_install and self.result_message is None:
            self.timed_out = True
            self.cancel.setEnabled(False)
            self.process.kill()

    def cancel_download(self):
        if (self.process is not None and
                self.process.state() != QProcess.ProcessState.NotRunning and
                self.cancel.isEnabled()):
            self.progress_message = "Cancelling stalled download…"
            self.cancel.setEnabled(False)
            self.process.kill()

    def process_error(self, error):
        if self.process is not None and error == QProcess.ProcessError.FailedToStart:
            self.error_message = "Could not start the update worker."

    def update_finished(self, exit_code, exit_status):
        self.read_messages()
        self.heartbeat.stop()
        successful = (
            exit_code == 0 and
            exit_status == QProcess.ExitStatus.NormalExit and
            self.result_message is not None
        )
        if successful:
            changed = self.result_message.startswith("1:")
            self.changed = changed
            self.status.setText(self.result_message[2:])
        elif self.timed_out:
            self.status.setText(
                "Update timed out before installing anything.\n"
                "Check your internet/VPN connection to GitHub, then try again.")
        else:
            self.status.setText(
                "Update failed: " +
                (self.error_message or "The update process stopped unexpectedly.") +
                "\nYour saved pets have not been deleted.")
        self.wait_pid = None
        self.action.setText("▶ Launch Ghost Pet" if self.changed else "↻ Retry update")
        self.action.setEnabled(True)
        self.close_button.setEnabled(True)
        self.cancel.hide()
        self.process = None

    def closeEvent(self, event):
        if (self.process is not None and
                self.process.state() != QProcess.ProcessState.NotRunning):
            event.ignore()
            return
        super().closeEvent(event)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait-pid", type=int, default=None)
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    dialog = UpdaterDialog(wait_pid=args.wait_pid)
    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
