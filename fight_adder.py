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
    fighter_one_name: str, 
    fighter_two_name: str, 
    winner_name: str, 
    date: str, 
    weight_class: str, 
    draw: bool, 
    no_contest: bool, 
    championship_fight: bool, 
    fighter_data: dict,
    prediction_factors_file="prediction_factors.json",
    log_actions=True
) -> None:
    """Adds fight with given data to given fighter data dict (fighter_data). 

    Also updates fighter's elo. Championship fight status as an odds factor 
    remains to be implemented.

    Args:
        fighter_one_name (str): 
            name of first fighter
        fighter_two_name (str): 
            name of second fighter
        winner_name (str): 
            name of winner. If draw or no contest, the winner is still either 
            fighter_one_name or fighter_two_name, randomly.
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
        prediction_factors_file (str, optional):
            the path to the prediction_factors.json file. Defaults to 
            "prediction_factors.json".
        log_actions (bool, optional):
            whether or not to log actions to action_log.txt. Used for debugging.
            Defaults to False.

    Returns:
        None
    """
    
    def log_action(action: str) -> None: 
        if not log_actions: return
        with open(ACTION_LOG, "a") as f:
            try: 
                f.write(action+"\n")
            except UnicodeEncodeError:
                f.write("UnicodeEncodeError")

    # remove spaces from weight class to be consistent with other data
    weight_class = weight_class.replace(" ", "")
    weight_class = weight_class.replace("’", "'")

    DEFAULT_ELO = 1500

    fighter_one: Fighter = Fighter(fighter_one_name, 0, {})
    fighter_two: Fighter = Fighter(fighter_two_name, 0, {})
    fighter_results = [0.5, 0.5]

    # if fighters are not in fighter_data, add them
    for fighter_name in (fighter_one_name, fighter_two_name):
        try:
            fighter_data[fighter_name]
        except KeyError:
            fighter_data[fighter_name] = {
                "elo": DEFAULT_ELO,
                "record": {},
            }
            log_action(f"Fighter {fighter_name} not found in fighter data, adding to fighter data")

    # get get data from fighter_data and put it in the fighter objects
    # also puts results in fighter_results
    for i, fighter in enumerate([fighter_one, fighter_two]):
        individual_fighter_data = fighter_data[fighter.name]

        fighter.elo = float(individual_fighter_data["elo"])
        fighter.record = individual_fighter_data["record"]

        if not draw and not no_contest: fighter_results[i] = int(fighter.name == winner_name)     

    #  calculate new elos (no need to update fighter objects; it messes up calculation and changing fighter objects isn't needed anymore)
    new_elos = [0, 0]
    for i, fighter in enumerate([fighter_one, fighter_two]):
        other = fighter_two if i == 0 else fighter_one
        if other == fighter_one: fighter_one_new_elo = fighter.elo

        fighter_has_less_than_two_fights = len(fighter.record) < 2
        if not no_contest: new_elos[i] = fighter.elo+elo_change(fighter.get_odds(other, date, prediction_factors_file=prediction_factors_file), fighter_results[i], fighter_has_less_than_two_fights, prediction_factors_file=prediction_factors_file)

    for i, fighter in enumerate([fighter_one, fighter_two]):
        other = fighter_two if i == 0 else fighter_one
        log_action(f"Updating {fighter.name}'s elo to {fighter.elo}")
        fighter_data[fighter.name]["elo"] = new_elos[i]

        # add fight to fighter's record
        # if the date is in the fighter record, make another date called date + "j" where j is the number of times that date has been used
        if date in fighter.record:
            j = 1
            while date+str(j) in fighter.record: j += 1
            date = date+str(j)

        fighter_data[fighter.name]["record"][date] = {
            "opponent": other.name,
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

class Fighter:
    def __init__(self, name: str, elo: float, record: dict):
        self.name: str = name
        self.elo: float = elo
        self.record: dict = record
    
    def get_fighter_weight_class(self):
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
        for date, fight_data in self.record.items():
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

    def get_last_fight_was_loss(self):
        try:
            last_fight = list(self.record.values())[-1]
            if last_fight["result"] == 0: return True
        except IndexError:
            pass
        return False
    
    def get_months_since_last_fight(self, date):
        try:
            last_fight_date = list(self.record.keys())[-1]
            last_fight_month = last_fight_date.split(" ")[0]
            last_fight_year = last_fight_date.split(" ")[2]
            MONTH_NUMBERS = {
                "Jan": 1,
                "Feb": 2,
                "Mar": 3,
                "Apr": 4,
                "May": 5,
                "Jun": 6,
                "Jul": 7,
                "Aug": 8,
                "Sep": 9,
                "Oct": 10,
                "Nov": 11,
                "Dec": 12,
            }
            last_fight_month_number = MONTH_NUMBERS[last_fight_month]
            current_fight_month_number = MONTH_NUMBERS[date.split(" ")[0]]
            return (current_fight_month_number-last_fight_month_number) % 12
        except IndexError:
            return 0

    def get_odds(self, other_fighter, date: str, prediction_factors_file="prediction_factors.json"):
        weight_class_ratio = calculate_weight_class_ratio(self.get_fighter_weight_class(), other_fighter.get_fighter_weight_class())
        return expected_odds(
            self.elo, 
            other_fighter.elo, 
            self.get_last_fight_was_loss(),
            other_fighter.get_last_fight_was_loss(),
            weight_class_ratio,
            self.get_months_since_last_fight(date),
            other_fighter.get_months_since_last_fight(date),
            prediction_factors_file=prediction_factors_file
        )

    def __str__(self):
        return f"{self.name} ({self.elo})"

if __name__ == "__main__":
    # copy training_fighter_data.json to test_fighter_data.json
    with open("training_fighter_data.json", "r") as f:
        fighter_data = json.load(f)
    with open("test_fighter_data.json", "w") as f:
        json.dump(fighter_data, f, indent=4)
    add_fight("Conor McGregor", "Dustin Poirier", "Dustin Poirier", "July 10, 2021", "Lightweight", False, False, False, fighter_data_file="test_fighter_data.json")