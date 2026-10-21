"""GUI regression: a roaming pet must never be painted in the house too."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import unittest
from unittest.mock import patch
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from ghostpet import PetState
from house import HouseDialog, HouseCanvas, TILE, W, H


class HousePresenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["ghostpet-presence"])

    def test_desktop_cat_is_never_rendered_indoors_even_with_stale_save_flag(self):
        state = PetState(
            name="Mochi", founder=True, egg_hatched=True,
            location="house", desktop_pet_id="cat_1",
            house_version=2, housewarming_granted=True,
            house_layout="cottage", unlocked_house_layouts=["cottage"],
            adopted_pets=[{"id":"cat_1","species":"Cat","name":"Pumpkin",
                           "x":12,"y":9,"location":"house"}],
            furniture=[], owned_furniture=["bed"],
        )
        house = HouseDialog(state, lambda:None, lambda:None, lambda:None)
        try:
            # Explicitly simulate a stale "house" flag after desktop summon.
            state.adopted_pets[0]["location"]="house"
            image=QImage(W*TILE,H*TILE,QImage.Format.Format_ARGB32)
            image.fill(0)
            with patch.object(HouseCanvas, "draw_housemate") as mocked:
                house.canvas.render(image)
                mocked.assert_not_called()
            # The same cat can be seen inside only after Founder is on desktop.
            state.desktop_pet_id="founder"
            state.location="desktop"
            house.refresh()
            image.fill(0)
            with patch.object(HouseCanvas, "draw_housemate") as mocked:
                house.canvas.render(image)
                mocked.assert_called_once()
        finally:
            house.close()


if __name__ == "__main__":
    unittest.main()
