import csv
import json
from odds_calculation_methods import expected_odds

FIGHT_DATA_FILE = "fight-data/remaining_ufc_fights.json"
FIGHTER_DATA_FILE = "fighter_data.csv"
OUTPUT_FILE = "fight-data/predictions.csv"

HEADER = "date,fighter1,fighter2,expected_odds_for_fighter1,result"

def write_fight_predictions(fight_data_file=FIGHT_DATA_FILE, output_file=OUTPUT_FILE, fighter_data_file=FIGHTER_DATA_FILE):
    # open fight-data/remaining_ufc_fights.json
    with open(fight_data_file, "r") as f:
        remaining_fights = json.load(f)
    with open(fighter_data_file, "r") as f:
        fighter_data = csv.DictReader(f)
        fighter_data = [fighter for fighter in fighter_data]

    fighter_elos = {}
    for fighter in fighter_data:
        fighter["fighter"] = fighter["fighter"].replace("\\", "")
        # get just the name and elo, cutting off the elo after the . in the string
        fighter_elos[fighter["fighter"]] = fighter["elo"][:fighter["elo"].index(".")]


    DEFAULT_ELO = 1500
    DATES_OF_FIGHTS_TO_CHECK = "Mar 27, 2021"

    prediction_reality_model = {
        0: {
            "match count": 0,
            "wins": 0,
        },
        5: {
            "match count": 0,
            "wins": 0,
        },
        10: {
            "match count": 0,
            "wins": 0,
        },
        15: {
            "match count": 0,
            "wins": 0,
        },
        20: {
            "match count": 0,
            "wins": 0,
        },
        25: {
            "match count": 0,
            "wins": 0,
        },
        30: {
            "match count": 0,
            "wins": 0,
        },
        35: {
            "match count": 0,
            "wins": 0,
        },
        40: {
            "match count": 0,
            "wins": 0,
        },
        45: {
            "match count": 0,
            "wins": 0,
        },
        50: {
            "match count": 0,
            "wins": 0,
        },
        55: {
            "match count": 0,
            "wins": 0,
        },
        60: {
            "match count": 0,
            "wins": 0,
        },
        65: {
            "match count": 0,
            "wins": 0,
        },
        70: {
            "match count": 0,
            "wins": 0,
        },
        75: {
            "match count": 0,
            "wins": 0,
        },
        80: {
            "match count": 0,
            "wins": 0,
        },
        85: {
            "match count": 0,
            "wins": 0,
        },
        90: {
            "match count": 0,
            "wins": 0,
        },
        95: {
            "match count": 0,
            "wins": 0,
        },
        100: {
            "match count": 0,
            "wins": 0,
        },
    }
    
    for date in remaining_fights:
        for fight, fight_data in remaining_fights[date].items():
            accent_characters = {
                'á': 'a',
                'é': 'e',
                'í': 'i',
                'ó': 'o',
                'ú': 'u',
                'ñ': 'n',
                'ç': 'c',
                'ł': 'l',
                'ř': 'r',
            }
            corrected_fighter_names = {
                "Jung Chan-sung": "Chan Sung Jung",
                "Sergey Spivak": "Serghei Spivac",
                "Dricus du Plessis": "Dricus Du Plessis",
            }
            fighter_one = fight_data["winner"]
            fighter_two = fight_data["loser"]
            for fighter in corrected_fighter_names:
                if fighter_one == fighter: fighter_one = corrected_fighter_names[fighter]
                if fighter_two == fighter: fighter_two = corrected_fighter_names[fighter]
            for character in accent_characters:
                fighter_one = fighter_one.replace(character, accent_characters[character])
                fighter_two = fighter_two.replace(character, accent_characters[character])
            fighter_one_elo = int(fighter_elos[fighter_one]) if fighter_one in fighter_elos else DEFAULT_ELO
            fighter_two_elo = int(fighter_elos[fighter_two]) if fighter_two in fighter_elos else DEFAULT_ELO
            expected_odds_for_fighter1 = expected_odds(fighter_one_elo, fighter_two_elo)
            expected_odds_for_fighter2 = 1 - expected_odds_for_fighter1

            prediction_is_strong = abs(expected_odds_for_fighter1-0.5) > 0.20

            if prediction_is_strong: 
                print (f"Fight: {fighter_one} - {fighter_one_elo} vs {fighter_two} - {fighter_two_elo}")
                if fight_data["draw"] == True: print("DRAW")
                else: print(f"Winner: {fight_data['winner']}")
                print(f"Expected Odds for {fight_data['winner']}: {expected_odds_for_fighter1}")
            

            # round the odds to the nearest multiple of 5
            fighter_one_rounded_odds = round(expected_odds_for_fighter1*100/5)*5
            fighter_two_rounded_odds = round(expected_odds_for_fighter2*100/5)*5
            fighter_one_won = fight_data["draw"] == False and fight_data["winner"] == fighter_one
            fighter_two_won = fight_data["draw"] == False and fight_data["winner"] == fighter_two
            prediction_reality_model[fighter_one_rounded_odds]["match count"] += 1
            prediction_reality_model[fighter_two_rounded_odds]["match count"] += 1
            if fighter_one_won: prediction_reality_model[fighter_one_rounded_odds]["wins"] += 1
            if fighter_two_won: prediction_reality_model[fighter_two_rounded_odds]["wins"] += 1
        
    total_odds_difference = 0
    for odds, data in prediction_reality_model.items():
        if data["match count"] == 0: continue
        print(f"Odds: {odds}, Match Count: {data['match count']}, Wins: {data['wins']}, Win Percentage: {data['wins']/data['match count']}")
        total_odds_difference += abs(odds - data["wins"]/data["match count"]*100)

if __name__ == "__main__":
    write_fight_predictions()