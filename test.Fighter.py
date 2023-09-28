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
    def test_elo_one_win(self):
        self.assertEqual(fighters["Mr. One Win"].elo(), 1520)
        self.assertEqual(fighters["Mr. One Loss"].elo(), 1480)
        self.assertEqual(fighters["Mr. Drawer"].elo(), 1500)

    def test_default_record(self):
        self.assertEqual(default_fighter.wins, 0)
        self.assertEqual(default_fighter.draws, 0)
        self.assertEqual(default_fighter.losses, 0)

    def test_record_one_win(self):
        self.assertEqual(fighters["Mr. One Win"].wins, 1)
        self.assertEqual(fighters["Mr. One Win"].draws, 0)
        self.assertEqual(fighters["Mr. One Win"].losses, 0)

    def test_record_one_loss(self):
        self.assertEqual(fighters["Mr. One Loss"].wins, 0)
        self.assertEqual(fighters["Mr. One Loss"].draws, 0)
        self.assertEqual(fighters["Mr. One Loss"].losses, 1)

    def test_record_one_draw(self):
        self.assertEqual(fighters["Mr. Drawer"].wins, 0)
        self.assertEqual(fighters["Mr. Drawer"].draws, 1)
        self.assertEqual(fighters["Mr. Drawer"].losses, 0)

    def test_record_multiple_fights_one(self):
        self.assertEqual(fighters["Experienced Fighter"].wins, 3)
        self.assertEqual(fighters["Experienced Fighter"].draws, 0)
        self.assertEqual(fighters["Experienced Fighter"].losses, 2)

    def test_record_multiple_fights_two(self):
        self.assertEqual(fighters["Inexperienced Fighter"].wins, 0)
        self.assertEqual(fighters["Inexperienced Fighter"].draws, 1)
        self.assertEqual(fighters["Inexperienced Fighter"].losses, 2)

    def test_experience_attribute(self):
        self.assertEqual(default_fighter.experienced(), False)
        self.assertEqual(fighters["Inexperienced Fighter"].experienced(), False)
        self.assertEqual(fighters["Experienced Fighter"].experienced(), True)

# tests run when file is run
if __name__ == '__main__':
    unittest.main()
