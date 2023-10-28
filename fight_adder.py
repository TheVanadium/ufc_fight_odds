import csv
import json
from odds_calculation_methods import expected_odds, elo_change

FIGHTER_DATA_FILE = "fighter_data.json"
ACTION_LOG = "action_log.txt"

WEIGHT_CLASSES = {
        "Women'sStrawweight": 115,
        "Women'sFlyweight": 125,
        "Women'sBantamweight": 135,
        "Women'sFeatherweight": 145,
        "Strawweight": 115,
        "Flyweight": 125,
        "Bantamweight": 135,
        "Featherweight": 145,
        "Lightweight": 155,
        "Welterweight": 170,
        "Middleweight": 185,
        "LightHeavyweight": 205,
        "Heavyweight": 265,
    }

# no accents in fighter_one or fighter_two please
# winner is fighter_one or fighter_two, even if it's a draw
def add_fight(fighter_one: str, fighter_two: str, winner: str, date: str, weight_class: str, draw: bool, no_contest: bool, championship_fight: bool, fighter_data_file: str = FIGHTER_DATA_FILE):
    with open(fighter_data_file, "r") as f:
        fighter_data = json.load(f)

    # remove spaces from weight class to be consistent with other data
    weight_class = weight_class.replace(" ", "")
    weight_class = weight_class.replace("’", "'")

    DEFAULT_ELO = 1500
    fighter_elos = [DEFAULT_ELO, DEFAULT_ELO]
    fighter_weight_classes = ["", ""]
    fighter_odds = [0, 0]
    fighter_results = [0.5, 0.5]
    FIGHTER_ONE_INDEX = 0
    FIGHTER_TWO_INDEX = 1

    for fighter_name in (fighter_one, fighter_two):
        if fighter_name not in fighter_data:
            fighter_data[fighter_name] = {
                "elo": DEFAULT_ELO,
                "record": {},
            }
            # print (f"Fighter {fighter_name} not found in {fighter_data_file}, adding to {fighter_data_file}")
            with open(ACTION_LOG, "a") as f:
                f.write(f"Fighter {fighter_name} not found in {fighter_data_file}, adding to {fighter_data_file}\n")
            with open(fighter_data_file, "w") as f:
                json.dump(fighter_data, f, indent=4)

    for fighter_name, individual_fighter_data in fighter_data.items():
        if fighter_odds[FIGHTER_ONE_INDEX] != 0 and fighter_odds[FIGHTER_TWO_INDEX] != 0: break
        if fighter_name != fighter_one and (fighter_name != fighter_two): continue
        index = FIGHTER_ONE_INDEX
        if fighter_name == fighter_two: index = FIGHTER_TWO_INDEX

        fighter_elos[index] = float(individual_fighter_data["elo"])
        fighter_weight_classes[index] = get_fighter_weight_class(individual_fighter_data["record"])
        if fighter_weight_classes[index] == "": weight_class_ratio = 1
        else: 
            try: 
                weight_class_ratio = WEIGHT_CLASSES[fighter_weight_classes[index]] / WEIGHT_CLASSES[weight_class]
            except KeyError:
                weight_class_ratio = 1
        fighter_odds[index] = expected_odds(fighter_elos[index], fighter_elos[abs(index-1)], weight_class_ratio)

        if not draw and not no_contest: fighter_results[index] = int(fighter_name == winner)

    new_fighter_elos = [0, 0]
    for i in range(2):
        if fighter_odds[i] == 0: KeyError(f"Fighter {fighter_one} or {fighter_two} not found in {fighter_data_file}")
        fighter_has_less_than_two_fights = False
        for fighter_name in (fighter_one, fighter_two):
            if len(fighter_data[fighter_name]["record"]) < 2: fighter_has_less_than_two_fights = True
        k_factor = 32
        if fighter_has_less_than_two_fights: k_factor = 64
        new_fighter_elos[i] = fighter_elos[i]+elo_change(fighter_odds[i], fighter_results[i], k_factor=k_factor)
        if no_contest: new_fighter_elos[i] = fighter_elos[i]

    # update elos, add fight to fighter records
    for fighter_name in fighter_data:
        if fighter_name != fighter_one and (fighter_name != fighter_two): continue
        # print (f"Updating {fighter_name}'s elo from {fighter_data[fighter_name]['elo']} to {new_fighter_elos[FIGHTER_ONE_INDEX if fighter_name == fighter_one else FIGHTER_TWO_INDEX]}")
        with open(ACTION_LOG, "a") as f:
            f.write(f"Updating {fighter_name}'s elo from {fighter_data[fighter_name]['elo']} to {new_fighter_elos[FIGHTER_ONE_INDEX if fighter_name == fighter_one else FIGHTER_TWO_INDEX]}\n")
        index = FIGHTER_ONE_INDEX
        if fighter_name == fighter_two: index = FIGHTER_TWO_INDEX
        # add fight to fighter's record
        fighter_data[fighter_name]["elo"] = new_fighter_elos[index]
        fighter_data[fighter_name]["record"][date] = {
            "opponent": fighter_one if fighter_name == fighter_two else fighter_two,
            "result": fighter_results[index],
            "weight_class": weight_class,
        }
    
    with open(fighter_data_file, "w") as f:
        json.dump(fighter_data, f, indent=4)
        with open(ACTION_LOG, "a") as f:
            f.write(f"Fight between {fighter_one} and {fighter_two} on date {date} added to {fighter_data_file}\n")
        # print (f"Fight between {fighter_one} and {fighter_two} on date {date} added to {fighter_data_file}")
    return

# get last 2 fights chronologically (they're sorted first->last), then pick the lighter of the 2 weight classes, then return that
    # if there's catchweight, treat it as ""
    # if there's only 1 fight, return that weight class
    # if there's no fights, return ""
def get_fighter_weight_class(fighter_record: dict): 
    last_two_fights = []
    for date, fight_data in fighter_record.items():
        last_two_fights.append(fight_data)
        if len(last_two_fights) > 2: last_two_fights.pop(0)
    if len(last_two_fights) == 0: return ""
    if len(last_two_fights) == 1: return last_two_fights[0]["weight_class"]
    lighter_weight_class = ""
    lighter_weight_class_weight = 10000
    for fight in last_two_fights:
        if fight["weight_class"].startswith("Catch"): continue
        if WEIGHT_CLASSES[fight["weight_class"]] < lighter_weight_class_weight:
            lighter_weight_class = fight["weight_class"]
            lighter_weight_class_weight = WEIGHT_CLASSES[fight["weight_class"]]
    return lighter_weight_class    
    

if __name__ == "__main__":
    # copy fighter_data.json to test_fighter_data.json
    with open("fighter_data.json", "r") as f:
        fighter_data = json.load(f)
    with open("test_fighter_data.json", "w") as f:
        json.dump(fighter_data, f, indent=4)
    add_fight("Conor McGregor", "Dustin Poirier", "Dustin Poirier", "July 10, 2021", "Lightweight", False, False, False, fighter_data_file="test_fighter_data.json")