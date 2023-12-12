import json
from odds_calculation_methods import expected_odds, elo_change

FIGHTER_DATA_FILE = "training_fighter_data.json"
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

def add_fight(
    fighter_one: str, 
    fighter_two: str, 
    winner: str, 
    date: str, 
    weight_class: str, 
    draw: bool, 
    no_contest: bool, 
    championship_fight: bool, 
    fighter_data: dict
) -> None:
    """Adds fight with given data to given fighter data dict (fighter_data). 

    Also updates fighter's elo. Championship fight status as an odds factor 
    remains to be implemented.

    Args:
        fighter_one (str): 
            name of first fighter
        fighter_two (str): 
            name of second fighter
        winner (str): 
            name of winner. If draw or no contest, the winner is still either 
            fighter_one or fighter_two, randomly.
        date (str): 
            date of fight as a string. Format doesn't matter, but in the API, 
            it's MMM DD, YYYY, with the month being 3 letters and the day never 
            having leading zeroes.
        weight_class (str): 
            must be in WEIGHT_CLASSES. If not, weight will be ignored as a 
            factor in calculating odds.
        draw (bool): 
            whether or not the fight was a draw
        no_contest (bool): 
            whether or not the fight was a no contest
        championship_fight (bool): 
            whether or not the fight was a championship fight (not including 
            interim championships)
        fighter_data (dict):
            the dict to be modified. information formatted the same as 
            training_fighter_data.json, see documentation.md for details

    Returns:
        None
    """
    
    # remove spaces from weight class to be consistent with other data
    weight_class = weight_class.replace(" ", "")
    weight_class = weight_class.replace("’", "'")
    
    FIGHTER_ONE_INDEX = 0
    FIGHTER_TWO_INDEX = 1

    DEFAULT_ELO = 1500
    fighter_names = [fighter_one, fighter_two]
    fighter_elos = [DEFAULT_ELO, DEFAULT_ELO]
    fighter_weight_classes = ["", ""]
    fighter_last_fight_was_loss = [False, False]
    fighter_odds = [0, 0]
    fighter_results = [0.5, 0.5]

    # if fighters are not in fighter_data, add them
    for fighter_name in (fighter_one, fighter_two):
        try:
            fighter_data[fighter_name]
        except KeyError:
            fighter_data[fighter_name] = {
                "elo": DEFAULT_ELO,
                "record": {},
            }
            log_action(f"Fighter {fighter_name} not found in fighter data, adding to fighter data")

    # get elos, weight classes, odds, and results, and put them in the lists above
    for fighter_name in (fighter_one, fighter_two):
        current_fighter_index = FIGHTER_ONE_INDEX
        if fighter_name == fighter_two: current_fighter_index = FIGHTER_TWO_INDEX
        other_fighter_index = abs(current_fighter_index-1)

        individual_fighter_data = fighter_data[fighter_name]

        fighter_elos[current_fighter_index] = float(individual_fighter_data["elo"])
        
        fighter_weight_classes[current_fighter_index] = get_fighter_weight_class(individual_fighter_data["record"])
        if fighter_weight_classes[current_fighter_index] == "": weight_class_ratio = 1
        else: weight_class_ratio = calculate_weight_class_ratio(fighter_weight_classes[current_fighter_index], weight_class)
        
        # get fighter last fight was loss
        try:
            last_fight = list(individual_fighter_data["record"].values())[-1]
            if last_fight["result"] == 0: fighter_last_fight_was_loss[current_fighter_index] = True
        except IndexError:
            pass
        log_action(f"Fighter {fighter_name} last fight was loss: {fighter_last_fight_was_loss[current_fighter_index]}")
        
        # if both are filled in, calculate odds
        if fighter_weight_classes[FIGHTER_ONE_INDEX] != "" and fighter_weight_classes[FIGHTER_TWO_INDEX] != "":
            fighter_odds[current_fighter_index] = expected_odds(
                fighter_elos[current_fighter_index], 
                fighter_elos[other_fighter_index], 
                fighter_last_fight_was_loss[current_fighter_index],
                fighter_last_fight_was_loss[other_fighter_index],
                weight_class_ratio
            )
            fighter_odds[other_fighter_index] = 1-fighter_odds[current_fighter_index]

        if not draw and not no_contest: fighter_results[current_fighter_index] = int(fighter_name == winner)

    #  calculate new elos
    new_fighter_elos = [0, 0]
    for i in range(2):
        fighter_not_found = fighter_odds[i] == 0
        if fighter_not_found: KeyError(f"Fighter {fighter_one} or {fighter_two} not found in fighter data")
        log_action(f"fighter_not_found: {fighter_not_found}")
        fighter_has_less_than_two_fights = len(fighter_data[fighter_names[i]]["record"]) < 2
        new_fighter_elos[i] = fighter_elos[i]+elo_change(fighter_odds[i], fighter_results[i], fighter_has_less_than_two_fights)
        if no_contest: new_fighter_elos[i] = fighter_elos[i]
        log_action(f"Fighter {fighter_names[i]} has {len(fighter_data[fighter_names[i]]['record'])} fights, so their elo change is {elo_change(fighter_odds[i], fighter_results[i], fighter_has_less_than_two_fights)}")

    # update elos, add fight to fighter records
    for i, fighter_name in enumerate(fighter_names):
        log_action(f"Updating {fighter_name}'s elo from {fighter_data[fighter_name]['elo']} to {new_fighter_elos[i]}")
        # add fight to fighter's record
        fighter_data[fighter_name]["elo"] = new_fighter_elos[i]
        # if the date is in the fighter record, make another date called date + "j" where j is the number of times that date has been used
        if date in fighter_data[fighter_name]["record"]:
            j = 1
            while date+str(j) in fighter_data[fighter_name]["record"]: j += 1
            date = date+str(j)
        fighter_data[fighter_name]["record"][date] = {
            "opponent": fighter_names[abs(i-1)],
            "result": fighter_results[i],
            "weight_class": weight_class,
        }

# get last 2 fights chronologically (they're sorted first->last), then pick the lighter of the 2 weight classes, then return that
    # if there's catchweight, treat it as ""
    # if there's only 1 fight, return that weight class
    # if there's no fights, return ""
def get_fighter_weight_class(fighter_record: dict) -> str:
    """Gets the 'natural' weight class of the fighter, based on their last two 
        fights.
    
        Picks the lighter of the two weight classes.
    
    Args:
        fighter_record (dict): 
            fighter record from training_fighter_data.json

    Returns:
        str: 
            the 'natural' weight class of the fighter, based on their last two fights.
            the natural weight is the lighter of the two weight classes. 
            catchweight
            is considered blank and the other weight class is considered the natural 
            one.
            if the fighter had no fights, or only catchweight fights, returns ""

            Examples:
                weight_class_of_last_two_fights = ["Lightweight", "Welterweight"]
                returns "Lightweight"

                weight_class_of_last_two_fights = ["Catchweight", "Welterweight"]
                returns "Welterweight"

                weight_class_of_last_two_fights = ["Catchweight", "Catchweight"]
                returns ""

                weight_class_of_last_two_fights = ["Lightweight"]
                returns "Lightweight"

                weight_class_of_last_two_fights = []
                returns ""
    """

    last_two_fights = []
    for date, fight_data in fighter_record.items():
        last_two_fights.append(fight_data)
        if len(last_two_fights) > 2: last_two_fights.pop(0)
    if len(last_two_fights) == 0: return ""
    if len(last_two_fights) == 1: return last_two_fights[0]["weight_class"]
    lighter_weight_class = ""
    UNDEFINED_WEIGHT_CLASS_VALUE: int = 10000
    lighter_weight_class_weight: int = UNDEFINED_WEIGHT_CLASS_VALUE
    for fight in last_two_fights:
        try:
            fight_weight_class = WEIGHT_CLASSES[fight["weight_class"]]
        except KeyError:
            # account for "ultimate fighter 28 heavyweight tournament weight class"
            if "heavyweight" in fight["weight_class"].lower(): fight_weight_class = WEIGHT_CLASSES["Heavyweight"]
            else: continue
        if lighter_weight_class_weight <= WEIGHT_CLASSES[fight["weight_class"]]: continue
        lighter_weight_class = fight["weight_class"]
        lighter_weight_class_weight = WEIGHT_CLASSES[fight["weight_class"]]
    if lighter_weight_class_weight == UNDEFINED_WEIGHT_CLASS_VALUE: return ""
    return lighter_weight_class    
    
def calculate_weight_class_ratio(fighter_weight_class: str, fight_weight_class: str) -> float:
    """ This exists because the potential for a KeyError makes for a 
        bulky chunk of code in add_fight()."""
    try: 
        return WEIGHT_CLASSES[fighter_weight_class]/WEIGHT_CLASSES[fight_weight_class]
    except KeyError:
        return 1

def log_action(action: str) -> None: 
    with open(ACTION_LOG, "a") as f:
        try: 
            f.write(action+"\n")
        except UnicodeEncodeError:
            f.write("UnicodeEncodeError")
    return

if __name__ == "__main__":
    # copy training_fighter_data.json to test_fighter_data.json
    with open("training_fighter_data.json", "r") as f:
        fighter_data = json.load(f)
    with open("test_fighter_data.json", "w") as f:
        json.dump(fighter_data, f, indent=4)
    add_fight("Conor McGregor", "Dustin Poirier", "Dustin Poirier", "July 10, 2021", "Lightweight", False, False, False, fighter_data_file="test_fighter_data.json")