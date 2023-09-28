# unit test template
import unittest
import json

from Fighter import Fighter

# load test data    
with open("test_fighters.json", "r") as f:
    test_fighters = json.load(f)

default_fighter = Fighter("")
# key: str = fighter name, value: Fighter = fighter object
fighters: dict  = {}

for fighter_name in test_fighters:
    current_fighter_object: Fighter = Fighter(fighter_name, test_fighters[fighter_name]["region"])
    for opponent, fight_data in test_fighters[fighter_name]["fight_record"].items():
        current_fighter_object.add_fight(opponent, fight_data["result"], fight_data["location"], fight_data["date"])
    fighters[fighter_name] = current_fighter_object
    
class TestFighter(unittest.TestCase):
    default_fighter = Fighter("")
    def test_default_elo(self):
        self.assertEqual(default_fighter.elo(), 1500)

    # all these fights assume same home region
    def test_elo_one_fight(self):
        self.assertEqual(fighters["Mr. One Win"].elo(), 1520)
        self.assertEqual(fighters["Mr. One Loss"].elo(), 1480)
        self.assertEqual(fighters["Mr. Drawer"].elo(), 1500)

    def test_experience_attribute(self):
        self.assertEqual(default_fighter.experienced(), False)
        self.assertEqual(fighters["Inexperienced Fighter"].experienced(), False)
        self.assertEqual(fighters["Experienced Fighter"].experienced(), True)

    def test_last_fight_attribute(self):
        self.assertEqual(default_fighter.last_fight(), None)
        self.assertEqual(fighters["Mr. One Win"].last_fight(), "Win")
        self.assertEqual(fighters["Mr. One Loss"].last_fight(), "Loss")
        self.assertEqual(fighters["Mr. Drawer"].last_fight(), "Draw")

# tests run when file is run
if __name__ == '__main__':
    unittest.main()
