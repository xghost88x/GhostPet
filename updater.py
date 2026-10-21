#!/usr/bin/env python3
"""Small PySide6 update window. The download and installation run off the UI thread."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys

from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout,
)
from updater_core import update_app


class UpdateWorker(QThread):
    progress = Signal(str)
    result = Signal(str, bool, bool)

    def __init__(self, root, wait_pid=None):
        super().__init__()
        self.root = root
        self.wait_pid = wait_pid

    def run(self):
        try:
            text, changed = update_app(self.root, self.progress.emit, self.wait_pid)
            self.result.emit(text, changed, True)
        except Exception as error:
            self.result.emit(f"Update failed: {error}", False, False)


class UpdaterDialog(QDialog):
    def __init__(self, wait_pid=None):
        super().__init__()
        self.root = Path(__file__).resolve().parent
        self.wait_pid = wait_pid
        self.worker = None
        self.changed = False
        self.setWindowTitle("Ghost Pet • Update Center")
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background: #f7eedf; color: #494238; }
            QLabel { color: #494238; font-size: 14px; }
            QPushButton { background: #769b80; color: white;
              border-radius: 8px; padding: 11px; font-weight: bold; }
            QPushButton:hover { background: #5c7e67; }
        """)
        layout = QVBoxLayout(self)
        title = QLabel("🐭  Ghost Pet Update Center")
        title.setStyleSheet("font-size: 21px; font-weight: bold;")
        layout.addWidget(title)
        version_path = self.root / "VERSION"
        current = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "unknown"
        layout.addWidget(QLabel(f"Installed version: {current}"))
        self.status = QLabel(
            "Check GitHub for the latest changes.\n"
            "Your pets, furniture, coins, and local save will be preserved."
        )
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        row = QHBoxLayout()
        self.action = QPushButton("↻ Check and install updates")
        self.action.clicked.connect(self.action_clicked)
        row.addWidget(self.action)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        row.addWidget(self.close_button)
        layout.addLayout(row)
        if wait_pid:
            QTimer.singleShot(150, self.start_update)

    def action_clicked(self):
        if self.changed:
            try:
                subprocess.Popen([str(self.root / "start.sh")], cwd=str(self.root),
                                 start_new_session=True)
            except OSError as exc:
                self.status.setText(f"Could not reopen Ghost Pet: {exc}")
                return
            self.close()
        else:
            self.start_update()

    def start_update(self):
        if self.worker is not None and self.worker.isRunning():
            return
        self.changed = False
        self.status.setText("Getting the latest version…")
        self.action.setEnabled(False)
        self.close_button.setEnabled(False)
        self.worker = UpdateWorker(self.root, self.wait_pid)
        self.worker.progress.connect(self.status.setText)
        self.worker.result.connect(self.finished)
        self.worker.start()

    def finished(self, message, changed, success):
        self.status.setText(message)
        self.changed = changed
        self.wait_pid = None
        self.action.setText("▶ Launch Ghost Pet" if changed else "↻ Check again")
        self.action.setEnabled(True)
        self.close_button.setEnabled(True)

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            event.ignore()  # Do not interrupt an in-progress file replacement.
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
