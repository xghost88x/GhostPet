"""Smoke-check Windows packaging paths, clean onboarding and release-updater safety."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile

from PySide6.QtWidgets import QApplication

import ghostpet
import windows_updater


class WindowsBetaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication(["ghostpet-win-ci"])

    def test_clean_windows_state_gets_600_coins_and_no_preview_gift(self):
        with patch.object(ghostpet,"WINDOWS_BETA",True):
            state=ghostpet.PetState()
        self.assertEqual(state.coins,600)
        self.assertTrue(state.preview_coins_claimed)
        self.assertFalse(state.egg_hatched)
        self.assertIsNone(state.adopted_pets)

    def test_old_save_is_respected_and_not_reset_to_600(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with patch.object(ghostpet,"WINDOWS_BETA",True), \
                 patch.object(ghostpet,"DATA_DIR",root), \
                 patch.object(ghostpet,"STATE_FILE",root/"state.json"):
                old=ghostpet.PetState()
                old.coins=112
                old.egg_hatched=True
                old.adopted_pets=[{"id":"cat-1","name":"Pumpkin","species":"Cat"}]
                old.save()
                restored=ghostpet.PetState.load()
                self.assertEqual(restored.coins,112)
                self.assertEqual(restored.adopted_pets[0]["name"],"Pumpkin")

    def test_windows_release_channel_never_installs_linux_source(self):
        other={"tag_name":"v0.8.0","draft":False,"assets":[{
            "name":windows_updater.ASSET_NAME,"state":"uploaded"
        }]}
        found={"tag_name":"windows-beta-v0.8.0-beta","draft":False,
               "assets":[{"name":windows_updater.ASSET_NAME,"state":"uploaded"}]}
        release,asset=windows_updater.latest_beta([other,found])
        self.assertEqual(release["tag_name"],found["tag_name"])
        self.assertEqual(asset["name"],windows_updater.ASSET_NAME)

    def test_updater_rejects_zip_traversal_and_unknown_payloads(self):
        for filename in ("../sneaky.exe","GhostPet-Windows/state.json",
                         "GhostPet-Windows/../../hidden.exe"):
            with self.subTest(filename=filename):
                data=io.BytesIO()
                with zipfile.ZipFile(data,"w") as archive:
                    archive.writestr(filename,b"danger")
                with self.assertRaises(ValueError):
                    windows_updater.unpack_release(data.getvalue())

    def test_update_only_replaces_whitelisted_app_and_preserves_state(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)
            (directory/"GhostPet.exe").write_bytes(b"old app")
            (directory/"state.json").write_text('{"coins":193}')
            files={
                "GhostPet.exe":b"new app",
                "GhostPetUpdater.exe":b"new updater",
                "VERSION":b"0.8.0-beta\n",
            }
            windows_updater.install_files(directory,files,lambda _:None)
            self.assertEqual((directory/"GhostPet.exe").read_bytes(),b"new app")
            self.assertEqual((directory/"GhostPetUpdater.exe").read_bytes(),b"new updater")
            self.assertEqual((directory/"state.json").read_text(),'{"coins":193}')

    def test_offscreen_windows_pet_house_and_friendship_render(self):
        state=ghostpet.PetState(
            name="Founder",egg_hatched=True,founder=True,
            coins=600,adopted_pets=[
                {"id":"cat-1","name":"Pumpkin","species":"Cat","x":12,"y":8}
            ],furniture=[],owned_furniture=["bed"],
            unlocked_house_layouts=["cottage"], relationships={}
        )
        roaming=ghostpet.RoamingPet(state)
        try:
            roaming.show()
            roaming.open_console()
            self.assertTrue(roaming.invite_selected_buddy("cat-1"))
            self.assertTrue(roaming.buddy.isVisible())
            roaming.open_house()
            self.assertTrue(roaming.house_dialog.friend_selector.isEnabled())
            self.assertEqual(state.coins,600)
        finally:
            if roaming.house_dialog:roaming.house_dialog.close()
            if roaming.console:roaming.console.close()
            roaming.buddy.close()
            roaming.portal.close()
            roaming.close()


if __name__=="__main__":
    unittest.main()
