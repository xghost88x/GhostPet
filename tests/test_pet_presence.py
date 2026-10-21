"""Persisted pet identity is separate from the roaming window and Founder state."""
import copy
import unittest
from types import SimpleNamespace
from pet_presence import (FOUNDER, NONE, current_pet, bring_to_desktop,
                          send_desktop_pet_home, repair_presence)


class HouseholdPresenceTests(unittest.TestCase):
    def setUp(self):
        self.state = SimpleNamespace(
            name="Original Mouse", coins=117, hunger=79,
            species="Ghost", color="Mint", location="desktop",
            desktop_pet_id="founder",
            adopted_pets=[
                {"id":"cat1","name":"Pumpkin","species":"Cat","hunger":46,"x":10,"y":8},
                {"id":"dragon1","name":"Ember","species":"Dragon","hunger":66,"x":12,"y":8},
            ],
        )
        repair_presence(self.state)

    def test_summon_adopted_and_send_home(self):
        original = (self.state.name, self.state.coins, self.state.hunger,
                    self.state.species, self.state.color)
        cat = bring_to_desktop(self.state,"cat1")
        self.assertEqual(cat["name"],"Pumpkin")
        self.assertEqual(self.state.location,"house")
        self.assertEqual(self.state.desktop_pet_id,"cat1")
        self.assertEqual(cat["location"],"desktop")
        self.assertEqual(self.state.adopted_pets[1]["location"],"house")
        self.assertIs(current_pet(self.state),cat)
        send_desktop_pet_home(self.state)
        self.assertEqual(cat["location"],"house")
        self.assertIs(current_pet(self.state),False)
        self.assertEqual(self.state.desktop_pet_id,NONE)
        self.assertEqual((self.state.name, self.state.coins, self.state.hunger,
                          self.state.species, self.state.color),original)

    def test_switch_back_to_founder_preserves_adopted_stats(self):
        before = copy.deepcopy(self.state.adopted_pets)
        bring_to_desktop(self.state, "dragon1")
        self.assertEqual(self.state.desktop_pet_id,"dragon1")
        bring_to_desktop(self.state, FOUNDER)
        self.assertIsNone(current_pet(self.state))
        self.assertEqual(self.state.location,"desktop")
        self.assertTrue(all(p["location"]=="house" for p in self.state.adopted_pets))
        self.assertEqual([p["hunger"] for p in self.state.adopted_pets],
                         [p["hunger"] for p in before])

    def test_legacy_indoor_founder_does_not_appear_outside(self):
        self.state.location = "house"
        self.state.desktop_pet_id = "founder"
        repair_presence(self.state)
        self.assertEqual(self.state.desktop_pet_id,NONE)
        self.assertIs(current_pet(self.state),False)

    def test_absent_adopted_id_rejected(self):
        with self.assertRaises(ValueError):
            bring_to_desktop(self.state,"unknown")

    def test_restores_exactly_one_existing_desktop_pet(self):
        self.state.desktop_pet_id = "cat1"
        self.state.location = "desktop"
        for p in self.state.adopted_pets:
            p["location"] = "desktop"
        repair_presence(self.state)
        self.assertEqual(self.state.location,"house")
        self.assertEqual([p["location"] for p in self.state.adopted_pets],
                         ["desktop","house"])


if __name__ == "__main__":
    unittest.main()
