"""Desktop cursor antics: bounded navigation, state preservation and UI controls."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import time
import unittest
from unittest.mock import patch

from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QApplication
from ghostpet import (
    PetState, RoamingPet, NONE, CURSOR_GAP,
    cursor_chase_destination,
)


class CursorChaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["ghostpet-cursor"])

    def setUp(self):
        self.state=PetState(
            name="Mochi", egg_hatched=True, founder=True,
            desktop_pet_id="founder",desktop_companion_id="none",
            housewarming_granted=True,house_version=2, relationships={},
            adopted_pets=[{"id":"cat1","name":"Pumpkin","species":"Cat",
                           "sleeping":False,"happiness":55,"x":12,"y":9}],
            furniture=[],owned_furniture=["bed"],
            unlocked_house_layouts=["cottage"],
        )
        self.roam=RoamingPet(self.state)
        self.roam.show()
        self.roam.open_console()

    def tearDown(self):
        self.roam.stop_cursor_chase(celebrate=False)
        if self.roam.console: self.roam.console.close()
        if self.roam.house_dialog: self.roam.house_dialog.close()
        self.roam.buddy.close()
        self.roam.portal.close()
        self.roam.close()

    def test_chase_target_stays_outside_cursor_and_on_screen(self):
        screen=QRect(0,0,960,640)
        widget=self.roam
        for point in (QPoint(100,100),QPoint(800,300),QPoint(5,400),
                      QPoint(955,600),QPoint(450,2),QPoint(450,639)):
            with self.subTest(point=point):
                target=cursor_chase_destination(widget,point,screen)
                self.assertIsNotNone(target)
                self.assertGreaterEqual(target.x(),screen.left())
                self.assertGreaterEqual(target.y(),screen.top())
                self.assertLessEqual(target.x()+widget.width(),screen.right()+1)
                self.assertLessEqual(target.y()+widget.height(),screen.bottom()+1)
                rect=QRect(target,widget.size())
                self.assertFalse(rect.contains(point),"Pet must not cover pointer")
                self.assertTrue(
                    target.x()+widget.width()+CURSOR_GAP<=point.x() or
                    target.x()>=point.x()+CURSOR_GAP
                )

    def test_select_cat_then_click_manual_chase_and_happiness_once(self):
        self.roam.invite_selected_buddy("cat1")
        self.roam.console.selected_id="cat1"
        self.roam.console.refresh()
        self.assertTrue(self.roam.console.chase_button.isEnabled())
        self.roam.console.chase_button.click()
        self.assertEqual(self.roam.cursor_chaser_id,"cat1")
        self.assertFalse(self.roam.console.isVisible())
        current=self.roam.buddy.pos()
        screen=QApplication.primaryScreen().availableGeometry()
        point=QPoint(max(screen.left()+160,min(screen.right()-160,current.x()+250)),
                     max(screen.top()+100,min(screen.bottom()-100,current.y()+100)))
        self.roam.advance_cursor_chase(point)
        self.assertNotEqual(self.roam.buddy.pos(),current)
        self.assertGreater(self.roam.cursor_chase_until,time.monotonic())
        before=self.state.adopted_pets[0]["happiness"]
        self.roam.cursor_chase_until=time.monotonic()-1
        self.roam.advance_cursor_chase(point)
        self.assertEqual(self.roam.cursor_chaser_id,NONE)
        self.assertEqual(self.state.adopted_pets[0]["happiness"],before+2)
        self.roam.advance_cursor_chase(point)
        self.assertEqual(self.state.adopted_pets[0]["happiness"],before+2)

    def test_auto_cursor_antics_toggle_and_no_automatic_chase_when_disabled(self):
        self.roam.console.cursor_toggle.click()
        self.assertFalse(self.state.auto_cursor_chase)
        self.assertIn("Off",self.roam.console.cursor_toggle.text())
        self.roam.last_cursor_chase=0
        with patch("ghostpet.random.random",return_value=0):
            self.assertFalse(self.roam.maybe_start_cursor_chase())
        self.assertEqual(self.roam.cursor_chaser_id,NONE)
        # Toggle controls *only* spontaneous starts. Manually playing still works.
        self.assertTrue(self.roam.start_cursor_chase("founder",manual=True))
        self.roam.stop_cursor_chase(celebrate=False)
        self.roam.console.show()
        self.roam.console.cursor_toggle.click()
        self.assertTrue(self.state.auto_cursor_chase)

    def test_sleeping_and_cuddling_pets_cannot_chase(self):
        self.state.sleeping=True
        self.assertFalse(self.roam.start_cursor_chase("founder"))
        self.state.sleeping=False
        self.roam.cuddle_mode=True
        self.assertFalse(self.roam.start_cursor_chase("founder"))
        self.roam.cuddle_mode=False
        self.assertTrue(self.roam.start_cursor_chase("founder"))
        self.roam.going_home=True
        self.roam.advance_cursor_chase(QPoint(400,300))
        self.assertEqual(self.roam.cursor_chaser_id,NONE)

    def test_pair_interactions_do_not_interrupt_cursor_game(self):
        self.roam.invite_selected_buddy("cat1")
        self.assertTrue(self.roam.start_cursor_chase("cat1"))
        self.assertFalse(self.roam.pair_ready())
        self.assertFalse(self.roam.start_pair_interaction("play"))
        self.roam.dismiss_buddy()
        self.assertEqual(self.roam.cursor_chaser_id,NONE)


if __name__ == "__main__":
    unittest.main()
