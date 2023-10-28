import unittest
import json
from fight_adder import add_fight

REAL_FILE = "fighter_data.json"
TEST_FILE = "test_fighter_data.json"

class TestFightAdder(unittest.TestCase):
    with open("fighter_data.json", "r") as f:
        json_data = f.read()
    with open(TEST_FILE, "w") as f:
        f.write(json_data)

    def test_two_veteran_fighters(self):
        add_fight("Conor McGregor", "Dustin Poirier", "Dustin Poirier", "July 10, 2035", "Lightweight", False, False, True, fighter_data_file=TEST_FILE)
        with open(TEST_FILE, "r") as f:
            json_data = f.read()
        json_data = json.loads(json_data)
        self.assertTrue("July 10, 2035" in json_data["Conor McGregor"]["record"])

    def test_one_debut_fighter(self):
        add_fight("Pink Unicorn", "Alexander Volkanovski", "Alexander Volkanovski", "July 10, 2021", "Lightweight", False, False, True, fighter_data_file=TEST_FILE)
        with open(TEST_FILE, "r") as f:
            json_data = f.read()
        json_data = json.loads(json_data)
        self.assertTrue("July 10, 2021" in json_data["Pink Unicorn"]["record"])
        
if __name__ == '__main__':
    unittest.main()