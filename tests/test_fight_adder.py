import unittest
import json

import sys
sys.path.append("..")
from fight_adder import add_fight

FIGHTER_DATA_FILE = "../training_fighter_data.json"
PREDICTION_FACTORS_FILE = "../prediction_factors.json"

class TestFightAdder(unittest.TestCase):
    def test_two_veteran_fighters_date_added_loser(self):
        with open(FIGHTER_DATA_FILE, "r") as f:
            training_fighter_data = f.read()
        training_fighter_data = json.loads(training_fighter_data)
        add_fight(
            "Conor McGregor", 
            "Dustin Poirier", 
            "Dustin Poirier", 
            "Jul 10, 2035", 
            "Lightweight", 
            False, 
            False, 
            True, 
            fighter_data=training_fighter_data,
            prediction_factors_file=PREDICTION_FACTORS_FILE
        )
        self.assertTrue(training_fighter_data["Conor McGregor"]["record"]["Jul 10, 2035"]["result"] == 0)

    def test_two_veteran_fighters_date_added_winner(self):
        with open(FIGHTER_DATA_FILE, "r") as f:
            training_fighter_data = f.read()
        training_fighter_data = json.loads(training_fighter_data)
        add_fight(
            "Conor McGregor", 
            "Dustin Poirier", 
            "Dustin Poirier", 
            "Jul 10, 2035", 
            "Lightweight", 
            False, 
            False, 
            True, 
            fighter_data=training_fighter_data,
            prediction_factors_file=PREDICTION_FACTORS_FILE
        )
        self.assertTrue(training_fighter_data["Dustin Poirier"]["record"]["Jul 10, 2035"]["result"] == 1)

    def test_two_veteran_fighters_elo_updated_loss(self):
        with open(FIGHTER_DATA_FILE, "r") as f:
            training_fighter_data = f.read()
        training_fighter_data = json.loads(training_fighter_data)
        old_elo: float = training_fighter_data["Conor McGregor"]["elo"]
        add_fight(
            "Conor McGregor", 
            "Dustin Poirier", 
            "Dustin Poirier", 
            "Jul 10, 2035", 
            "Lightweight", 
            False, 
            False, 
            True, 
            fighter_data=training_fighter_data,
            prediction_factors_file=PREDICTION_FACTORS_FILE
        )
        self.assertTrue(training_fighter_data["Conor McGregor"]["elo"] < old_elo)

    def test_two_veteran_fighters_elo_updated_win(self):
        with open(FIGHTER_DATA_FILE, "r") as f:
            training_fighter_data = f.read()
        training_fighter_data = json.loads(training_fighter_data)
        old_elo: float = training_fighter_data["Dustin Poirier"]["elo"]
        add_fight(
            "Conor McGregor", 
            "Dustin Poirier", 
            "Dustin Poirier", 
            "Jul 10, 2035", 
            "Lightweight", 
            False, 
            False, 
            True, 
            fighter_data=training_fighter_data,
            prediction_factors_file=PREDICTION_FACTORS_FILE
        )
        self.assertTrue(training_fighter_data["Dustin Poirier"]["elo"] > old_elo)

    def test_two_new_fighters_date_added_winner(self):
        with open(FIGHTER_DATA_FILE, "r") as f:
            training_fighter_data = f.read()
        training_fighter_data = json.loads(training_fighter_data)
        with open(PREDICTION_FACTORS_FILE, "r") as f:
            prediction_factors = f.read()
        prediction_factors = json.loads(prediction_factors)
        add_fight(
            "Fake Fighter 1",
            "Fake Fighter 2",
            "Fake Fighter 1",
            "Feb 11, 2064",
            "Heavyweight",
            False,
            False,
            True,
            fighter_data=training_fighter_data,
            prediction_factors_file=PREDICTION_FACTORS_FILE
        )
        self.assertTrue(training_fighter_data["Fake Fighter 1"]["record"]["Feb 11, 2064"]["result"] == 1)

    def test_two_new_fighters_date_added_loser(self):
        with open(FIGHTER_DATA_FILE, "r") as f:
            training_fighter_data = f.read()
        training_fighter_data = json.loads(training_fighter_data)
        with open(PREDICTION_FACTORS_FILE, "r") as f:
            prediction_factors = f.read()
        prediction_factors = json.loads(prediction_factors)
        add_fight(
            "Fake Fighter 1",
            "Fake Fighter 2",
            "Fake Fighter 1",
            "Feb 11, 2064",
            "Heavyweight",
            False,
            False,
            True,
            fighter_data=training_fighter_data,
            prediction_factors_file=PREDICTION_FACTORS_FILE
        )
        self.assertTrue(training_fighter_data["Fake Fighter 2"]["record"]["Feb 11, 2064"]["result"] == 0)

    def test_two_new_fighters_elo_updated_winner(self):
        with open(FIGHTER_DATA_FILE, "r") as f:
            training_fighter_data = f.read()
        training_fighter_data = json.loads(training_fighter_data)
        with open(PREDICTION_FACTORS_FILE, "r") as f:
            prediction_factors = f.read()
        prediction_factors = json.loads(prediction_factors)
        # the elo change should be half the newcomer k-factor as the odds are 50/50
        DEFAULT_ELO = 1500
        correct_winner_elo = DEFAULT_ELO + 0.5*prediction_factors["newcomer_k-factor"]
        add_fight(
            "Fake Fighter 1",
            "Fake Fighter 2",
            "Fake Fighter 1",
            "Feb 11, 2064",
            "Heavyweight",
            False,
            False,
            True,
            fighter_data=training_fighter_data,
            prediction_factors_file=PREDICTION_FACTORS_FILE
        )
        self.assertTrue(training_fighter_data["Fake Fighter 1"]["elo"] == correct_winner_elo)

    def test_two_new_fighters_elo_updated_loser(self):
        with open(FIGHTER_DATA_FILE, "r") as f:
            training_fighter_data = f.read()
        training_fighter_data = json.loads(training_fighter_data)
        with open(PREDICTION_FACTORS_FILE, "r") as f:
            prediction_factors = f.read()
        prediction_factors = json.loads(prediction_factors)

        # the elo change should be half the newcomer k-factor as the odds are 50/50
        DEFAULT_ELO = 1500
        correct_loser_elo = DEFAULT_ELO - 0.5*prediction_factors["newcomer_k-factor"]
        add_fight(
            "Fake Fighter 1",
            "Fake Fighter 2",
            "Fake Fighter 1",
            "Feb 11, 2064",
            "Heavyweight",
            False,
            False,
            True,
            fighter_data=training_fighter_data,
            prediction_factors_file=PREDICTION_FACTORS_FILE
        )
        self.assertTrue(training_fighter_data["Fake Fighter 2"]["elo"] == correct_loser_elo)

if __name__ == '__main__':
    unittest.main()