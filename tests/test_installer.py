"""Smoke-test the one-time desktop launcher installer in an isolated HOME."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class InstallerTests(unittest.TestCase):
    def test_installs_menu_desktop_icon_without_touching_save(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            (home / "Desktop").mkdir()
            save = home / ".local/share/ghostpet/state.json"
            save.parent.mkdir(parents=True)
            save.write_text('{"name":"My Founder Mouse"}', encoding="utf-8")
            env = os.environ.copy()
            env["HOME"] = str(home)
            env["XDG_CONFIG_HOME"] = str(home / ".config")
            run = subprocess.run(
                ["bash", str(source / "install.sh")],
                cwd=source, env=env, capture_output=True, text=True,
                timeout=35,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            app = home / "Applications/GhostPet"
            self.assertTrue((app / "start.sh").is_file())
            self.assertTrue((app / "updater.py").is_file())
            self.assertTrue((app / "update.sh").is_file())
            self.assertTrue(os.access(app / "start.sh", os.X_OK))
            entry = (home / ".local/share/applications/org.ghostpet.GhostPet.desktop").read_text()
            self.assertIn("Name=Ghost Pet", entry)
            self.assertIn(str(app / "start.sh"), entry)
            self.assertIn("Actions=Update;", entry)
            self.assertTrue((home / ".local/share/applications/org.ghostpet.Updater.desktop").exists())
            self.assertTrue((home / ".local/share/icons/hicolor/scalable/apps/ghostpet.svg").exists())
            self.assertEqual(save.read_text(encoding="utf-8"), '{"name":"My Founder Mouse"}')


if __name__ == "__main__":
    unittest.main()
