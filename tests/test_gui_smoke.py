"""Offscreen Qt smoke checks: the app must render and summon the chosen pet."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import tempfile
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter

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
                image = QImage(W*TILE,H*TILE,QImage.Format.Format_ARGB32)
                image.fill(0)
                painter = QPainter(image)
                try:
                    pet.house_dialog.canvas.render(painter)
                finally:
                    painter.end()
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
