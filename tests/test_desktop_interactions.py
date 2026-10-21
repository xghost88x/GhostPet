"""Actual two-window desktop interactions and hidden room labels regression."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import time
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from ghostpet import PetState, RoamingPet
from pet_presence import relationship_score


class DesktopInteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["ghostpet-pair-action-test"])

    def setUp(self):
        self.state = PetState(
            name="Mochi", founder=True, egg_hatched=True,
            adopted_pets=[{
                "id":"cat1", "name":"Pumpkin", "species":"Cat",
                "happiness":60, "energy":70, "x":12, "y":8,
            }],
            house_version=2, housewarming_granted=True,
            furniture=[], owned_furniture=["bed"],
            unlocked_house_layouts=["cottage"],
            desktop_pet_id="founder", desktop_companion_id="none",
            relationships={},
        )
        self.lead=RoamingPet(self.state)
        self.lead.show()
        self.lead.open_console()
        self.assertTrue(self.lead.invite_selected_buddy("cat1"))

    def tearDown(self):
        if self.lead.house_dialog:
            self.lead.house_dialog.close()
        if self.lead.console:
            self.lead.console.close()
        self.lead.buddy.close()
        self.lead.portal.close()
        self.lead.close()

    def test_play_button_bounces_and_rewards_relationship_once(self):
        score=relationship_score(self.state,"founder","cat1")
        self.assertTrue(self.lead.console.pair_play_button.isEnabled())
        self.lead.console.pair_play_button.click()
        self.assertEqual(self.lead.pair_interaction,"play")
        self.assertEqual(relationship_score(self.state,"founder","cat1"),score)
        self.assertFalse(self.lead.start_pair_interaction("play"))
        self.lead.pair_interaction_until=time.monotonic()-1
        self.lead.advance_pair_interaction()
        self.assertIsNone(self.lead.pair_interaction)
        self.assertGreater(relationship_score(self.state,"founder","cat1"),score)
        self.assertGreater(self.state.adopted_pets[0]["happiness"],60)
        new_score=relationship_score(self.state,"founder","cat1")
        self.lead.advance_pair_interaction()
        self.assertEqual(relationship_score(self.state,"founder","cat1"),new_score)

    def test_nuzzling_physically_moves_buddy_closer(self):
        self.assertTrue(self.lead.start_pair_interaction("nuzzle"))
        self.lead.buddy.move(self.lead.x()+145,self.lead.y()+32)
        before=abs(self.lead.buddy.x()-self.lead.x())
        for _ in range(4):
            self.lead.buddy.advance()
        self.assertLess(abs(self.lead.buddy.x()-self.lead.x()),before)
        self.lead.pair_interaction_until=0
        self.lead.advance_pair_interaction()
        self.assertIsNone(self.lead.pair_interaction)

    def test_send_buddy_home_cancels_bond_reward(self):
        score=relationship_score(self.state,"founder","cat1")
        self.assertTrue(self.lead.start_pair_interaction("chase"))
        self.lead.dismiss_buddy()
        self.assertIsNone(self.lead.pair_interaction)
        self.lead.advance_pair_interaction()
        self.assertEqual(relationship_score(self.state,"founder","cat1"),score)
        self.assertFalse(self.lead.buddy.isVisible())

    def test_cannot_play_while_one_pet_is_sleeping(self):
        self.state.adopted_pets[0]["sleeping"]=True
        self.assertFalse(self.lead.start_pair_interaction("greet"))
        self.assertFalse(self.lead.console.pair_ready() if hasattr(self.lead.console,"pair_ready") else self.lead.pair_ready())

    def test_auto_interactions_start_after_cooldown(self):
        geometry=QApplication.primaryScreen().availableGeometry()
        self.lead.move(geometry.left()+80,geometry.top()+80)
        self.lead.buddy.move(geometry.left()+176,geometry.top()+80)
        self.lead.last_friend_interaction=time.monotonic()-40
        self.assertTrue(self.lead.pair_ready())
        with patch.object(self.lead.buddy,"advance"), \
             patch("ghostpet.random.random",return_value=0.01):
            self.lead.animate()
        self.assertIn(self.lead.pair_interaction,("greet","nuzzle","play","chase"))

    def test_art_has_no_room_name_text(self):
        art = (Path(__file__).resolve().parents[1] / "cottage_art.py").read_text()
        self.assertNotIn("drawText(",art)
        self.assertNotIn("SLEEPING NOOK",art)
        self.assertNotIn("OPEN LIVING + DINING",art)
        self.assertNotIn("SUNLIT GLASS GARDEN",art)


if __name__ == "__main__":
    unittest.main()
