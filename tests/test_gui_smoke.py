"""Offscreen Qt smoke checks: the app must render and summon the chosen pet."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import tempfile
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

from ghostpet import PetState, RoamingPet
from house import TILE, W, H


class GhostPetGuiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["ghostpet-smoke"])

    def test_house_render_and_switch_desktop_pet(self):
        with tempfile.TemporaryDirectory() as temp:
            state = PetState(
                name="Founder Mouse", founder=True, egg_hatched=True, color="Mint",
                adopted_pets=[{"id":"cat1","name":"Fuzz","species":"Cat","x":13,"y":8}],
                furniture=[{"cell":2*W+3,"item":"bed"}],
                owned_furniture=["bed"],
                house_version=2, housewarming_granted=True,
                unlocked_house_layouts=["cottage"], house_layout="cottage",
            )
            pet = RoamingPet(state)
            try:
                pet.open_console()
                pet.console.selector.setCurrentIndex(1)
                pet.console.summon_button.click()
                self.assertEqual(state.desktop_pet_id, "cat1")
                self.assertEqual(state.location, "house")
                self.assertEqual(state.adopted_pets[0]["location"], "desktop")
                self.assertTrue(pet.isVisible())

                pet.open_house()
                balance = state.coins
                pet.house_dialog.claim_preview_coins()
                self.assertEqual(state.coins, balance + 600)
                self.assertTrue(state.preview_coins_claimed)
                pet.house_dialog.claim_preview_coins()
                self.assertEqual(state.coins, balance + 600,
                                 "Preview gift must only be claimable once")
                # Exercise actual visible buttons, not merely unlock helpers.
                house = pet.house_dialog
                house.layout_selector.setCurrentIndex(1)
                self.assertIn("120", house.layout_button.text())
                house.layout_button.click()
                self.assertEqual(state.house_layout, "open", house.status.text())
                self.assertEqual(state.coins, balance + 480)
                self.assertEqual(len(state.furniture), 1)
                self.assertEqual(state.furniture[0]["item"], "bed")
                self.assertNotEqual(house.entry_tile(state.furniture[0]), (3,2),
                                    "Bought furniture should move away from new built-ins")
                self.assertIn("Open Plan", house.status.text())
                house.layout_selector.setCurrentIndex(2)
                house.layout_button.click()
                self.assertEqual(state.house_layout, "garden", house.status.text())
                self.assertEqual(state.coins, balance + 220)
                # Switching to an owned layout must remain free.
                house.layout_selector.setCurrentIndex(0)
                house.layout_button.click()
                self.assertEqual(state.house_layout, "cottage", house.status.text())
                self.assertEqual(state.coins, balance + 220)
                self.assertLessEqual(house.canvas.width(), W*TILE)
                self.assertLessEqual(house.canvas.height(), H*TILE)
                self.assertGreater(house.canvas.zoom, 0)
                image = QImage(W*TILE,H*TILE,QImage.Format.Format_ARGB32)
                image.fill(0)
                pet.house_dialog.canvas.render(image)
                sampled = {
                    image.pixel(x,y)
                    for x in range(4, W*TILE, 9)
                    for y in range(4, H*TILE, 9)
                }
                self.assertGreater(len(sampled), 30, "Cottage artwork looks unrendered")

                pet.console.selector.setCurrentIndex(0)
                pet.console.summon_button.click()
                self.assertEqual(state.desktop_pet_id, "founder")
                self.assertEqual(state.location, "desktop")
                self.assertEqual(state.adopted_pets[0]["location"], "house")
                self.assertEqual(state.name, "Founder Mouse")
                self.assertEqual(state.adopted_pets[0]["name"], "Fuzz")
            finally:
                if pet.house_dialog:
                    pet.house_dialog.close()
                if pet.console:
                    pet.console.close()
                pet.portal.close()
                pet.close()


if __name__ == "__main__":
    unittest.main()
