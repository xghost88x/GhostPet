"""Regression: v0.5.4 updater initially copies only old module names."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class OlderUpdaterCompatibilityTests(unittest.TestCase):
    def test_old_updater_files_still_import_without_new_modules(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for name in ("ghostpet.py", "house.py", "activities.py", "nursery.py"):
                shutil.copy2(root / name, tmp_path / name)
            env = os.environ.copy()
            env["QT_QPA_PLATFORM"] = "offscreen"
            env["PYTHONPATH"] = str(tmp_path)
            command = (
                "import ghostpet,house;"
                "assert callable(ghostpet.bring_to_desktop);"
                "assert callable(ghostpet.draw_adopted_pet);"
                "assert callable(house.pixel_cottage);"
                "assert callable(house.current_pet)"
            )
            result = subprocess.run(
                [sys.executable, "-c", command],
                cwd=tmp_path, env=env, capture_output=True, text=True, timeout=20
            )
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__ == "__main__":
    unittest.main()
