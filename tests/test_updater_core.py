"""Update safety tests without internet access or a graphical display."""
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

from updater_core import REQUIRED, archive_files, update_app


def fake_archive(extra=None):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", zipfile.ZIP_DEFLATED) as z:
        for file in REQUIRED:
            z.writestr(f"GhostPet-commit/{file}", b"new contents")
        if extra:
            z.writestr(extra, b"bad")
    return data.getvalue()


class UpdateSafetyTests(unittest.TestCase):
    def test_accepts_expected_layout(self):
        result = archive_files(fake_archive())
        self.assertTrue(REQUIRED.issubset(result))
        self.assertEqual(result["ghostpet.py"], b"new contents")

    def test_rejects_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            archive_files(fake_archive("GhostPet-commit/../../escape.py"))

    def test_rejects_oversized_zip_member(self):
        from updater_core import MAX_SINGLE_FILE
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, "w") as z:
            for file in REQUIRED:
                z.writestr(f"GhostPet-commit/{file}", b"x")
            z.writestr("GhostPet-commit/README.md", b"b"*(MAX_SINGLE_FILE+1))
        with self.assertRaisesRegex(ValueError, "too large"):
            archive_files(bio.getvalue())

    def test_update_keeps_pet_save_and_venv(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            app = root / "Applications" / "GhostPet"
            app.mkdir(parents=True)
            (app / "start.sh").write_text("previous launcher", encoding="utf8")
            (app / "ghostpet.py").write_text("old founder sprite", encoding="utf8")
            venv = app / ".venv"
            venv.mkdir()
            (venv / "marker.txt").write_text("KEEP ME", encoding="utf8")
            save = root / "data" / "ghostpet" / "state.json"
            save.parent.mkdir(parents=True)
            save.write_text('{"name": "Founder", "coins": 245}', encoding="utf8")
            with (mock.patch.dict(os.environ, {"XDG_DATA_HOME": str(root / "data"), "HOME": str(root)}),
                  mock.patch("updater_core.latest_revision", return_value="a"*40),
                  mock.patch("updater_core.request_bytes", return_value=fake_archive()),
                  mock.patch("updater_core.other_running_instance", return_value=False),
                  mock.patch("updater_core.Path.home", return_value=root)):
                message, changed = update_app(app)
            self.assertTrue(changed)
            self.assertIn("Updated successfully", message)
            self.assertEqual(save.read_text(), '{"name": "Founder", "coins": 245}')
            self.assertEqual((venv / "marker.txt").read_text(), "KEEP ME")
            self.assertEqual((app / "ghostpet.py").read_bytes(), b"new contents")
            self.assertEqual((app / ".previous-version" / "ghostpet.py").read_text(), "old founder sprite")
            self.assertTrue(list((save.parent / "backups").glob("state-before-update-*.json")))
            self.assertEqual((app / ".ghostpet-revision").read_text().strip(), "a"*40)


if __name__ == "__main__":
    unittest.main()
