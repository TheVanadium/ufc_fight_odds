import json
from odds_calculation_methods import expected_odds
from fight_adder import get_fighter_weight_class, add_fight

FIGHT_DATA_FILE = "fight-data-collector/fight_data_2023.json"
FIGHTER_DATA_FILE = "fighter_data.json"
OUTPUT_FILE = "predictions.json"

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

PRINT_DEBUG: bool = False

def write_fight_predictions(fight_data_file=FIGHT_DATA_FILE, output_file=OUTPUT_FILE, fighter_data_file=FIGHTER_DATA_FILE) -> None:
    # get fight and fighter data
    # create dictionary to store fight predictions
    with open(fight_data_file) as f:
        fight_data = json.load(f)
    fight_data = dict(reversed(list(fight_data.items()))) # fights are in reverse chronological order in file, so reverse them to predict fights in order
    with open(fighter_data_file) as f:
        fighter_data = json.load(f)

    fight_predictions = {}

    # for each fight
        # get fighter data
        # calculate expected odds
        # store fight prediction in dictionary
        # update fighter's records
    for date, event_data in fight_data.items():
        for fight, individual_fight_data in event_data.items(): 
            if PRINT_DEBUG: print(fight)
            try:
                winner_elo = fighter_data[individual_fight_data["winner"]]["elo"]
            except KeyError:
                winner_elo = 1500
            try:
                loser_elo = fighter_data[individual_fight_data["loser"]]["elo"]
            except KeyError:
                loser_elo = 1500
            winner_weight_ratio = get_weight_ratio(
                individual_fight_data["winner"], 
                individual_fight_data["loser"], 
                individual_fight_data["weight_class"], 
                fighter_data
            )
            odds_for_winner = expected_odds(
                winner_elo, 
                loser_elo, 
                target_opponent_weight_ratio=winner_weight_ratio
            )
            # round odds to the nearest 0.05, then append result to fight_predictions[odds]
            # also do the inverse, as the odds of the loser winning are the inverse of the odds of the winner winning

            from decimal import Decimal
            rounded_odds_for_winner = Decimal(round(Decimal(odds_for_winner*20)))/20
            if PRINT_DEBUG: print(rounded_odds_for_winner)
            rounded_odds_for_loser = 1-rounded_odds_for_winner

            if float(rounded_odds_for_winner) not in fight_predictions:
                fight_predictions[float(rounded_odds_for_winner)] = []
            if float(rounded_odds_for_loser) not in fight_predictions:
                fight_predictions[float(rounded_odds_for_loser)] = []

            # should append a 1 to the winner's list and a 0 to the loser's list, unless draw is true, in which case append 0.5 to both lists
            # ignore no_contest fights
            if not individual_fight_data["no_contest"]:
                if individual_fight_data["draw"]:
                    fight_predictions[float(rounded_odds_for_winner)].append(0.5)
                    fight_predictions[float(rounded_odds_for_loser)].append(0.5)
                else:
                    fight_predictions[float(rounded_odds_for_winner)].append(1)
                    fight_predictions[float(rounded_odds_for_loser)].append(0)

            # update fighter records
            add_fight(
                fighter_one=individual_fight_data["winner"],
                fighter_two=individual_fight_data["loser"],
                winner=individual_fight_data["winner"],
                date=date,
                weight_class=individual_fight_data["weight_class"],
                draw=individual_fight_data["draw"],
                no_contest=individual_fight_data["no_contest"],
                championship_fight=individual_fight_data["championship_fight"],
                fighter_data=fighter_data
            ) 

    with open(output_file, "w") as f:
        json.dump(fight_predictions, f)

def get_weight_ratio(fighter_one: str, fighter_two: str, bout_weight_class: str, fighter_data: dict) -> float:
    """
        Computes the ratio of the weight classes of two fighters.
        If either fighter is debuting, their weight class is assumed to be the bout weight class.
        If the bout weight class is not in WEIGHT_CLASSES, the ratio is assumed to be 1.
        
        Args:
            fighter_one: name of the first fighter
            fighter_two: name of second fighter
            bout_weight_class: string containing the weight class of the bout
            fighter_data: dictionary containing fighter data
                (see documentation.md's description of fighter_data.json for format)

        Returns:
            The ratio of the weight classes of the two fighters.
    """
    
    # if bout weight class is catchweight or weird or something, make it a default value of 1
    if bout_weight_class.replace(" ", "") not in WEIGHT_CLASSES: return 1

    try: 
        fighter_one_record = fighter_data[fighter_one]["record"]
    except KeyError:
        fighter_one_record = {}
    try: 
        fighter_two_record = fighter_data[fighter_two]["record"]
    except KeyError:
        fighter_two_record = {}

    try:
        fighter_one_weight_class = get_fighter_weight_class(fighter_one_record)
    except KeyError:
        fighter_one_weight_class = bout_weight_class
    if fighter_one_weight_class not in WEIGHT_CLASSES: fighter_one_weight_class = bout_weight_class
    # need to remove spaces from weight class names to be consistent with other data
    fighter_one_weight_class = fighter_one_weight_class.replace(" ", "")
    try:
        fighter_two_weight_class = get_fighter_weight_class(fighter_two_record)
    except KeyError:
        fighter_two_weight_class = bout_weight_class
    if fighter_two_weight_class not in WEIGHT_CLASSES: fighter_two_weight_class = bout_weight_class
    fighter_two_weight_class = fighter_two_weight_class.replace(" ", "")
    
    return WEIGHT_CLASSES[fighter_one_weight_class] / WEIGHT_CLASSES[fighter_two_weight_class]

# basic function that reads prediction file, spits out result by adding all wins and losses in each key and dividing by total number of fights, spitting out key-value pairs of odds and win percentage
def get_win_percentage(fight_predictions_file=OUTPUT_FILE) -> dict:
    """
        Computes the win percentage of each fighter based on the fight predictions in a file.
        
        Args:
            fight_predictions_file: name of the file containing fight predictions
                (see documentation.md's description of test_predictions.json for format)

        Returns:
            A dictionary containing the win percentage of each fighter.
    """
    with open(fight_predictions_file) as f:
        fight_predictions = json.load(f)

    win_percentages = {}

    for odds, results in fight_predictions.items():
        win_percentages[odds] = sum(results)/len(results)

    return win_percentages

def get_standard_deviation(fight_predictions_file=OUTPUT_FILE) -> float:
    """
        Computes the standard deviation of the win percentages of each fighter based on the fight predictions in a file.
        
        Args:
            fight_predictions_file: name of the file containing fight predictions
                (see documentation.md's description of test_predictions.json for format)

        Returns:
            The standard deviation of the win percentages of each fighter.
    """
    with open(fight_predictions_file) as f:
        fight_predictions = json.load(f)

    predictions = []
    for odds, results in fight_predictions.items():
        for i in range(len(results)): predictions.append(float(odds))

    mean = sum(predictions)/len(predictions)
    variance = sum([(x-mean)**2 for x in predictions])/len(predictions)
    standard_deviation = variance**0.5

    return standard_deviation

def brier_skill_score(fight_predictions_and_results: dict) -> float:
    """
        Computes the Brier skill score of a set of fight predictions.
        
        Args:
            fight_predictions_and_results: dictionary containing fight predictions and results
                {
                    odd%: result%,
                    odd%: result%,
                }
            odd% being the predicted result of a fight, and result% being the percentage of fights won that were predicted to have odd%

        Returns:
            The Brier skill score of the fight predictions.
    """
    brier_skill_score = 0

    for odds, results in fight_predictions_and_results.items():
        brier_skill_score += (results - float(odds))**2

    brier_skill_score /= len(fight_predictions_and_results)

    return brier_skill_score

if __name__ == "__main__":
    ### TEST CODE ###
    # # write to test file that is copied from fighter_data.json
    # # this way, we can test the fight prediction generator without messing up the actual fighter data
    # with open(FIGHTER_DATA_FILE) as f:
    #     fighter_data = json.load(f)
    # with open("test_fighter_data.json", "w") as f:
    #     json.dump(fighter_data, f)
    # write_fight_predictions(fighter_data_file="test_fighter_data.json", output_file="test_predictions.json")
    # # write win percentage to file
    # with open("win_percentage.json", "w") as f:
    #     json.dump(get_win_percentage(), f)

    ### EXECUTION CODE ###
    # Note: Ensure test_fighter_data.json is a copy of fighter_data.json before running this code
    write_fight_predictions()

    if PRINT_DEBUG: 
        print (brier_skill_score(get_win_percentage()))
        print (get_standard_deviation())