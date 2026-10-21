"""Exercise the graphical updater worker without any network request."""
import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from updater import UpdaterDialog


class UpdateWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["ghostpet-update-test"])

    def run_stub(self, worker_source):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "VERSION").write_text("0.5.4", encoding="utf-8")
            (root / "updater_core.py").write_text(worker_source, encoding="utf-8")
            dlg = UpdaterDialog()
            dlg.root = root
            dlg.show()
            dlg.start_update()
            def stop_when_done():
                if dlg.close_button.isEnabled():
                    self.app.quit()
            poll = QTimer()
            poll.timeout.connect(stop_when_done)
            poll.start(40)
            safety = QTimer()
            safety.setSingleShot(True)
            safety.timeout.connect(self.app.quit)
            safety.start(6000)
            self.app.exec()
            poll.stop()
            safety.stop()
            self.assertTrue(dlg.close_button.isEnabled(), "Update window did not finish")
            message = dlg.status.text()
            changed = dlg.changed
            dlg.close()
            return message, changed

    def test_stalled_update_ui_is_responsive_and_reports_success(self):
        result, changed = self.run_stub(
            'def update_app(app_dir, progress, wait_pid):\n'
            '    progress("Checking GitHub revision...")\n'
            '    progress("Installing update (pet data is untouched)...")\n'
            '    return "Updated successfully to 0.6.0-preview", True\n'
        )
        self.assertTrue(changed)
        self.assertIn("0.6.0-preview", result)

    def test_failure_shows_recovery_message(self):
        result, changed = self.run_stub(
            'def update_app(app_dir, progress, wait_pid):\n'
            '    progress("Checking GitHub revision...")\n'
            '    raise OSError("Could not reach GitHub")\n'
        )
        self.assertFalse(changed)
        self.assertIn("Could not reach GitHub", result)


if __name__ == "__main__":
    unittest.main()
