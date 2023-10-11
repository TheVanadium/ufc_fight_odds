import csv
import json
from odds_calculation_methods import expected_odds

FIGHTER_DATA_FILE = "fighter_data.csv"

WEIGHT_CLASSES = {
        "Strawweight": 115,
        "Flyweight": 125,
        "Bantamweight": 135,
        "Featherweight": 145,
        "Lightweight": 155,
        "Welterweight": 170,
        "Middleweight": 185,
        "LightHeavyweight": 205,
        "Heavyweight": 265
    }

def add_fight(fighter_one: str, fighter_two: str, result: str, date: str, weight_class: str, draw: bool, no_contest: bool, championship_fight: bool, fighter_data_file: str = FIGHTER_DATA_FILE):
    with open(fighter_data_file, "r") as f:
        fighter_data = csv.DictReader(f)
        fighter_data = [fighter for fighter in fighter_data]

    DEFAULT_ELO = 1500
    fighter_elos = [DEFAULT_ELO, DEFAULT_ELO]
    fighter_weight_classes = ["", ""]
    fighter_odds = [0, 0]
    FIGHTER_ONE_INDEX = 0
    FIGHTER_TWO_INDEX = 1
    for fighter in fighter_data:
        if fighter["fighter"] != fighter_one and (fighter["fighter"] != fighter_two): continue
        index = FIGHTER_ONE_INDEX
        if fighter["fighter"] == fighter_two: index = FIGHTER_TWO_INDEX
        fighter_elos[index] = float(fighter["elo"])
        fighter_weight_classes[index] = get_fighter_weight_class(fighter["record"])
        weight_class_ratio = WEIGHT_CLASSES[fighter_weight_classes[index]] / WEIGHT_CLASSES[weight_class]
        fighter_odds[index] = expected_odds(fighter_elos[index], fighter_elos[abs(index-1)], weight_class_ratio)

    # update elos, add fight to fighter records
    for i, fighter in enumerate(fighter_data):
        if fighter["fighter"] != fighter_one and (fighter["fighter"] != fighter_two): continue
        index = FIGHTER_ONE_INDEX
        if fighter["fighter"] == fighter_two: index = FIGHTER_TWO_INDEX
        # insert at third last index, which is the last index of the record, minus the closing brackets and quote
        print("-------------------")
        print(fighter_data[i]["record"][:-1]) 
        fighter_data[i]["record"] = fighter_data[i]["record"][:-1]
        fighter_data[i]["record"] += f", \'{date}\'': "
        fighter_data[i]["record"] += f', {{\'opponent\': \'{fighter_two}\', \'result\': \'{result}\', \'weight_class\': \'{weight_class}\', \'draw\': {draw}, \'no_contest\': {no_contest}, \'championship_fight\': {championship_fight}}}]'

        fighter_data[i]["elo"] = fighter_elos[index]
    
    with (fighter_data_file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["fighter", "elo", "record"])
        writer.writeheader()
        writer.writerows(fighter_data)
    return

# set of key date, value dict of opponent, result, weight_class
def get_fighter_weight_class(fighter_record: str):
    # find the second last instance of "weight_class" in the string
    last_weight_class_index = fighter_record.rfind("weight_class")
    second_last_weight_class_index = fighter_record.rfind("weight_class", 0, last_weight_class_index)

    # skip the next 4 characters after weight_class, which are a `': '`, then get every character until the next `'`
    last_weight_class = fighter_record[last_weight_class_index + 16: fighter_record.index("'", last_weight_class_index + 16)]
    second_last_weight_class = fighter_record[second_last_weight_class_index + 16: fighter_record.index("'", second_last_weight_class_index + 16)]

    # pick the lighter of the two weight classes
    lighter_weight_class = last_weight_class if WEIGHT_CLASSES[last_weight_class] < WEIGHT_CLASSES[second_last_weight_class] else second_last_weight_class
    return lighter_weight_class


if __name__ == "__main__":
    add_fight("Conor McGregor", "Dustin Poirier", "win", "July 10, 2021", "Lightweight", False, False, True, fighter_data_file="test_fighter_data.csv")