"""House bowl servicing: food portions, hunger recovery and saved inventory."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import unittest
from PySide6.QtWidgets import QApplication
from ghostpet import PetState
from house import (
    HouseDialog, W, BOWL_CAPACITY, house_bowls, refill_house_bowls,
    house_feed_cycle, walls_for_layout, built_in_occupied,
)


class FoodBowlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["ghostpet-bowl-test"])

    def state(self, bowl_tile=(9,5)):
        return PetState(
            name="Mochi", egg_hatched=True, founder=True,
            hunger=30, house_version=2, housewarming_granted=True,
            location="house", desktop_pet_id="none", desktop_companion_id="none",
            adopted_pets=[
                {"id":"cat1","name":"Pumpkin","species":"Cat",
                 "hunger":42,"x":9,"y":4},
                {"id":"fox1","name":"Maple","species":"Fox",
                 "hunger":19,"x":9,"y":6},
            ],
            coins=500, furniture=[{"cell":bowl_tile[1]*W+bowl_tile[0],"item":"bowl"}],
            owned_furniture=["bowl"], unlocked_house_layouts=["cottage"],
            house_layout="cottage"
        )

    def test_old_bowls_migrate_full_and_two_pets_eat_once(self):
        state=self.state()
        self.assertEqual(house_bowls(state)[0]["servings"],BOWL_CAPACITY)
        self.assertEqual(house_feed_cycle(state,now=1000),["founder","cat1","fox1"])
        self.assertEqual([state.hunger,
                          state.adopted_pets[0]["hunger"],
                          state.adopted_pets[1]["hunger"]],[56,68,45])
        self.assertEqual(house_bowls(state)[0]["servings"],BOWL_CAPACITY-3)
        self.assertEqual(house_feed_cycle(state,now=1009),[])
        self.assertEqual(house_bowls(state)[0]["servings"],3)
        house_feed_cycle(state,now=1065)
        self.assertEqual(house_bowls(state)[0]["servings"],0)
        self.assertEqual(house_feed_cycle(state,now=1190),[])
        self.assertEqual(refill_house_bowls(state),1)
        self.assertEqual(house_bowls(state)[0]["servings"],6)
        self.assertEqual(state.coins,500)

    def test_outdoor_pets_do_not_use_indoor_bowl(self):
        state=self.state()
        state.desktop_pet_id="founder"
        state.desktop_companion_id="cat1"
        # Two pets on desktop. Only fox is eligible to eat inside.
        fed=house_feed_cycle(state,now=1000)
        self.assertEqual(fed,["fox1"])
        self.assertEqual(state.hunger,30)
        self.assertEqual(state.adopted_pets[0]["hunger"],42)
        self.assertEqual(state.adopted_pets[1]["hunger"],45)
        self.assertEqual(house_bowls(state)[0]["servings"],5)

    def test_consumption_requires_reachable_bowl_in_visible_house(self):
        state=self.state(bowl_tile=(12,9))
        self.assertEqual(house_feed_cycle(state,now=1000,require_near=True),[])
        state.house_pet_x,state.house_pet_y=12,8
        self.assertEqual(house_feed_cycle(state,now=1000,require_near=True),["founder"])
        self.assertEqual(house_bowls(state)[0]["servings"],5)

    def test_ui_refills_empty_bowl_without_spending_coins(self):
        state=self.state()
        house = HouseDialog(state,lambda:None,lambda:None,lambda:None)
        try:
            bowl=house_bowls(state)[0]
            bowl["servings"]=0
            house.refresh()
            self.assertIn("0/6",house.bowl_status.text())
            self.assertTrue(house.refill_button.isEnabled())
            house.refill_button.click()
            self.assertEqual(bowl["servings"],6)
            self.assertIn("6/6",house.bowl_status.text())
            self.assertIn("Refilled",house.status.text())
            self.assertEqual(state.coins,500)
            house.tile_clicked(house.entry_tile(bowl))
            self.assertIn("topped up",house.status.text())
        finally:
            house.close()

    def test_existing_bowl_servings_survive_layout_renovation(self):
        state=self.state(bowl_tile=(6,2))
        state.furniture[0]["servings"]=3
        house=HouseDialog(state,lambda:None,lambda:None,lambda:None)
        try:
            house.layout_selector.setCurrentIndex(1)
            house.choose_layout()
            self.assertEqual(state.house_layout,"open")
            self.assertEqual(len(house_bowls(state)),1)
            self.assertEqual(house_bowls(state)[0]["servings"],3)
            dest=house.entry_tile(house_bowls(state)[0])
            self.assertNotIn(dest,walls_for_layout("open"))
            self.assertNotIn(dest,built_in_occupied("open"))
            self.assertIn("bowl",state.owned_furniture)
        finally:
            house.close()

    def test_adopted_hunger_decays_while_house_closed(self):
        state=self.state()
        state.last_updated=1000
        state.advance(now=4600)
        self.assertLess(state.adopted_pets[0]["hunger"],42)


if __name__=="__main__":
    unittest.main()
