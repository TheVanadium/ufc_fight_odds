import unittest
from fighter_data_sorter import write_fighter_data

class TestFighterDataSorter(unittest.TestCase):
    write_fighter_data(output_file="test_fighter_data.csv")
    with open("test_fighter_data.csv", "r") as f:
        csv_data = f.readlines()

    def test_header(self):
        self.assertEqual(self.csv_data[0], "fighter,elo,record\n")

    # ufc 1 actually isn't in it rip
    def test_ufc_1_in_data_1(self):
        self.assertIn("Teila Tuli,", str(self.csv_data))

    def test_ufc_1_in_data_2(self):
        self.assertIn("November 12, 1993", str(self.csv_data))

    def test_ufc_2_in_data_1(self):
        self.assertIn("Scott Morris", str(self.csv_data))

    def test_ufc_2_in_data_2(self):
        self.assertIn("March 11, 1994", str(self.csv_data))

    # March 20, 2021 was last UFC event in dataset, Brunson vs Holland
    def test_ufc_brunson_vs_holland_in_data_1(self):
        self.assertIn("\\\'March 20, 2021\\\': {\\\'opponent\\\': \\\'Kevin Holland\\\'", str(self.csv_data))
        
    def test_ufc_brunson_vs_holland_in_data_2(self):
        self.assertIn("\\\'March 20, 2021\\\': {\\\'opponent\\\': \\\'Adrian Yanez\\\'", str(self.csv_data))

    delete_test_file = input("Delete test_fighter_data.csv? (y/n): ")
    if delete_test_file == "y":
        import os
        os.remove("test_fighter_data.csv")

if __name__ == '__main__':
    unittest.main()
