import unittest
import json
from fighter_data_sorter import write_fighter_data

TEST_FILE = "test_fighter_data.json"

class TestFighterDataSorter(unittest.TestCase):
    write_fighter_data(output_file=TEST_FILE)
    with open(TEST_FILE, "r") as f:
        json_data = f.read()

    json_data = json.loads(json_data)
    
    # ufc 1 is actually missing, so this test should fail until that changes
    def test_ufc_1_in_data(self):
        self.assertTrue("March 11, 1994" in self.json_data["Teila Tuli"]["record"])

    def test_ufc_2_in_data(self):
        self.assertTrue("March 11, 1994" in self.json_data["Scott Morris"]["record"])

    # leading 0 in month is important
    def test_ufc_136_in_data(self):
        self.assertTrue("October 08, 2011" in self.json_data["Chael Sonnen"]["record"])

    # no accents in names
    def test_ufc_136_no_accents_in_data(self):
        self.assertTrue("Jose Aldo" in self.json_data)

    # March 20, 2021 was last UFC event in dataset, Brunson vs Holland
    def test_ufc_brunson_vs_holland_date_in_data(self):
        self.assertTrue("March 20, 2021" in self.json_data["Kevin Holland"]["record"])

    delete_test_file = input("Delete test_fighter_data.json? (y/n): ")
    if delete_test_file == "y":
        import os
        os.remove("test_fighter_data.json")

if __name__ == '__main__':
    unittest.main()
