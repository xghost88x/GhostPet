"""Cuddle is visible in Pocket Care and rewards whichever pet was selected."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6.QtWidgets import QApplication

from ghostpet import PetState, RoamingPet


class CuddleControlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["ghostpet-cuddle-test"])

    def test_cuddle_button_works_for_adopted_and_founder(self):
        state = PetState(
            name="Mouse", egg_hatched=True, founder=True,
            housewarming_granted=True, unlocked_house_layouts=["cottage"],
            adopted_pets=[{"id":"cat1","name":"Pumpkin","species":"Cat",
                           "happiness":55,"affection":20,"x":13,"y":8}]
        )
        pet = RoamingPet(state)
        try:
            pet.open_console()
            buttons = [b for b in pet.console.findChildren(__import__("PySide6.QtWidgets",fromlist=["QPushButton"]).QPushButton)
                       if "Cuddle" in b.text()]
            self.assertTrue(buttons, "Cuddle should be visible in Pocket Care")
            pet.console.selector.setCurrentIndex(1)
            buttons[0].click()
            self.assertEqual(state.desktop_pet_id,"cat1")
            self.assertTrue(pet.cuddle_mode)
            for _ in range(5):
                pet.pat_directly()
            self.assertEqual(state.adopted_pets[0]["cuddles"],1)
            self.assertGreater(state.adopted_pets[0]["affection"],20)
            self.assertEqual(state.cuddles,0,"Founder cuddle stat must remain separate")
            pet.console.selector.setCurrentIndex(0)
            buttons[0].click()
            self.assertEqual(state.desktop_pet_id,"founder")
            self.assertTrue(pet.cuddle_mode)
            for _ in range(5):
                pet.pat_directly()
            self.assertEqual(state.cuddles,1)
        finally:
            if pet.console: pet.console.close()
            pet.portal.close()
            pet.close()


if __name__ == "__main__":
    unittest.main()
