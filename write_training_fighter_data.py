import json
from unidecode import unidecode
from fight_adder import add_fight

# there's some overlap in the training data i think, but it probably doesn't matter? since the fights should have the same key (date)
TRAINING_DATA_FILES = ["fight_data_pre_2023_a.json", "fight_data_pre_2023_b.json", "fight_data_pre_2023_c.json"]

def write_training_fighter_data(training_data_files: list = TRAINING_DATA_FILES, fighter_data_file: str = "fighter_data.json"):
    # if the fighter data file is empty, make it json-able
    try:
        with open(fighter_data_file, "r") as f:
            fighter_data = json.load(f)
    except json.decoder.JSONDecodeError:
        with open (fighter_data_file, "w") as f:
            json.dump({}, f, indent=4)

    # files are listed in reverse chronological order
    training_data_files.reverse()
    for training_data_file in training_data_files:
        with open("data-collector/" + training_data_file, "r") as f:
            training_data = json.load(f)

        # training data is in reverse chronological order, so we need to reverse it
        training_data = dict(reversed(list(training_data.items())))

        # "Jul 22, 2017": {
        #       "Fight: Chris Weidman vs Kelvin Gastelum": {
        #       "winner": "Chris Weidman",
        #       "loser": "Kelvin Gastelum",
        #       "weight_class": "Middleweight",
        #       "draw": false,
        #       "no_contest": false,
        #       "championship_fight": false
        #     },
        #       "Fight: Darren Elkins vs Dennis Bermudez": {
        #       "winner": "Darren Elkins",
        #       "loser": "Dennis Bermudez",
        #       "weight_class": "Featherweight",
        #       "draw": false,
        #       "no_contest": false,
        #       "championship_fight": false
        #     },
        #     ...
        
        for date, event_data in training_data.items():
            for fight_name, fight_data in event_data.items():
                winner = unidecode(fight_data["winner"])
                loser = unidecode(fight_data["loser"])
                weight_class = fight_data["weight_class"]
                draw = fight_data["draw"]
                no_contest = fight_data["no_contest"]
                championship_fight = fight_data["championship_fight"]
                add_fight(winner, loser, winner, date, weight_class, draw, no_contest, championship_fight, fighter_data_file)

if __name__ == "__main__":
    # create a header for the action log
    with open("action_log.txt", "w") as f:
        import datetime
        f.write("Testing at time: " + str(datetime.datetime.now()) + "\n")
    # clear fighter data file for testing
    with open("test_fighter_data.json", "w") as f:
        json.dump({}, f, indent=4)
    write_training_fighter_data(fighter_data_file="test_fighter_data.json")