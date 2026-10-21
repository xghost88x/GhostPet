"""Persistent pair bonds and two independent roaming companion windows."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import unittest
from PySide6.QtWidgets import QApplication

from ghostpet import PetState, RoamingPet
from pet_presence import (repair_presence, active_desktop_ids, invite_companion,
                          bring_to_desktop, send_desktop_pet_home,
                          send_companion_home, relationship_score,
                          strengthen_friendship, advance_house_friendships)


class DuoFriendshipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication(["ghostpet-duo-test"])

    def make_state(self):
        return PetState(
            name="Mochi", egg_hatched=True, founder=True,
            adopted_pets=[
                {"id":"cat1","name":"Pumpkin","species":"Cat","x":13,"y":8},
                {"id":"fox1","name":"Maple","species":"Fox","x":12,"y":9}],
            furniture=[],owned_furniture=["bed"],house_version=2,
            housewarming_granted=True,unlocked_house_layouts=["cottage"],
            desktop_pet_id="founder",desktop_companion_id="none",
            relationships={}
        )

    def test_two_pet_presence_and_promotion(self):
        state=self.make_state()
        repair_presence(state)
        self.assertTrue(invite_companion(state,"cat1"))
        self.assertEqual(active_desktop_ids(state),["founder","cat1"])
        self.assertEqual(state.adopted_pets[0]["location"],"desktop")
        self.assertEqual(state.adopted_pets[1]["location"],"house")
        send_desktop_pet_home(state)
        self.assertEqual(active_desktop_ids(state),["cat1"])
        self.assertEqual(state.location,"house")
        self.assertEqual(state.adopted_pets[0]["location"],"desktop")
        send_companion_home(state)
        self.assertEqual(active_desktop_ids(state),["cat1"])
        self.assertEqual(state.name,"Mochi")

    def test_pairs_grow_indoors_when_window_closed(self):
        state=self.make_state()
        repair_presence(state)
        before=relationship_score(state,"cat1","fox1")
        advance_house_friendships(state,6)
        self.assertGreater(relationship_score(state,"cat1","fox1"),before)
        self.assertEqual(relationship_score(state,"fox1","cat1"),
                         relationship_score(state,"cat1","fox1"))
        invite_companion(state,"cat1")
        current=relationship_score(state,"cat1","fox1")
        advance_house_friendships(state,6)
        self.assertEqual(current,relationship_score(state,"cat1","fox1"))
        strengthen_friendship(state,"founder","cat1",1000)
        self.assertEqual(relationship_score(state,"founder","cat1"),100)
        self.assertEqual(state.name,"Mochi")

    def test_real_second_window_and_house_friendship_meter(self):
        state=self.make_state()
        repair_presence(state)
        roaming=RoamingPet(state)
        try:
            roaming.show()  # main() does this in normal desktop launches.
            roaming.open_console()
            roaming.console.selector.setCurrentIndex(1)
            roaming.console.buddy_button.click()
            self.assertEqual(state.desktop_companion_id,"cat1")
            self.assertTrue(roaming.buddy.isVisible())
            self.assertTrue(roaming.isVisible())
            roaming.open_house()
            self.assertTrue(roaming.house_dialog.friend_selector.isEnabled())
            self.assertTrue(roaming.house_dialog.friend_selector.count()>=3)
            self.assertEqual(state.adopted_pets[0]["location"],"desktop")
            self.assertEqual(state.adopted_pets[1]["location"],"house")
            roaming.console.buddy_button.click()
            self.assertEqual(state.desktop_companion_id,"none")
            self.assertFalse(roaming.buddy.isVisible())
            roaming.invite_selected_buddy("cat1")
            self.assertEqual(state.desktop_companion_id,"cat1")
            roaming.send_home()
            self.assertEqual(state.desktop_pet_id,"cat1")
            self.assertEqual(state.desktop_companion_id,"none")
            self.assertTrue(roaming.isVisible())
            self.assertFalse(roaming.buddy.isVisible())
            self.assertEqual(state.location,"house")
        finally:
            if roaming.house_dialog:roaming.house_dialog.close()
            if roaming.console:roaming.console.close()
            roaming.buddy.close()
            roaming.portal.close()
            roaming.close()


if __name__=="__main__":
    unittest.main()
