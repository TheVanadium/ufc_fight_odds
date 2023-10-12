# elo system for the fighter data

import csv
import json

FIGHT_DATA_FILE = "chronological_total_fight_data.csv"
OUTPUT_FILE = "fighter_data.json"

def write_fighter_data(fight_data_file=FIGHT_DATA_FILE, output_file=OUTPUT_FILE):
    fighter_data = {}
    with (open(fight_data_file, "r")) as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        
        DATE_INDEX = -4
        WINNER_INDEX = -1
        WEIGHT_CLASS_INDEX = -2

        STANDARD_K_FACTOR = 32
        NOVEL_K_FACTOR = 48
        MAXIMUM_NUMBER_OF_FIGHTS_FOR_NOVEL_K_FACTOR = 2

        for row in reader:
            for fighter in (row[0], row[1]):
                if fighter not in fighter_data:
                    fighter_data[fighter] = {
                        "elo": 1500,
                        "record": {}
                    }
            
            for fighter in (row[0], row[1]):
                fighter_is_novel = len(fighter_data[fighter]["record"]) < MAXIMUM_NUMBER_OF_FIGHTS_FOR_NOVEL_K_FACTOR
                
                fighter_data[fighter]["record"][row[DATE_INDEX]] = {}
                fighter_data[fighter]["record"][row[DATE_INDEX]]["opponent"] = row[1] if fighter == row[0] else row[0]
                opponent_name = fighter_data[fighter]["record"][row[DATE_INDEX]]["opponent"]

                result: int = 1
                if row[WINNER_INDEX] == opponent_name: result = 0
                elif row[WINNER_INDEX] == "": result = 0.5
                fighter_data[fighter]["record"][row[DATE_INDEX]]["result"] = result

                # remove last 5 characters from weight class, it just says " Bout"
                current_bout_weight_class = row[WEIGHT_CLASS_INDEX][:-5]
                
                words_in_weight_classes_to_replace = {
                    "UFC": '',
                    "Interim": '',
                    "Title": '',
                    " ": ''
                }
                for word in words_in_weight_classes_to_replace: current_bout_weight_class = current_bout_weight_class.replace(word, '')
                fighter_data[fighter]["record"][row[DATE_INDEX]]["weight_class"] = current_bout_weight_class

                weight_classes = {
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
                fighter_opponent_weight_ratio = 1
                fight_number = 0
                for date, fight_data in fighter_data[fighter]["record"].items():

                    previous_weight_class = fight_data["weight_class"]
                    fight_number += 1
                    current_fight_is_in_last_two_fights = not fight_number < len(fighter_data[fighter]["record"]) - 3
                    if not current_fight_is_in_last_two_fights: continue

                    fight_is_in_fighters_usual_weight_class = previous_weight_class == current_bout_weight_class
                    if fight_is_in_fighters_usual_weight_class: continue
                    
                    current_fight_is_valid_weight_class = not previous_weight_class not in weight_classes
                    previous_weight_class_is_valid_weight_class = not current_bout_weight_class not in weight_classes
                    if not current_fight_is_valid_weight_class or not previous_weight_class_is_valid_weight_class: continue

                    fighter_opponent_weight_ratio = weight_classes[previous_weight_class]/weight_classes[current_bout_weight_class]
                    break

                current_elo = fighter_data[fighter]["elo"]
                opponent_name = fighter_data[fighter]["record"][row[DATE_INDEX]]["opponent"]
                opponent_elo = fighter_data[opponent_name]["elo"]

                current_fight_odds = expected_odds(current_elo, int(opponent_elo), target_opponent_weight_ratio=fighter_opponent_weight_ratio)
                k_factor = STANDARD_K_FACTOR
                if fighter_is_novel: k_factor = NOVEL_K_FACTOR
                fighter_data[fighter]["elo"] += elo_change(current_fight_odds, result, k_factor)

    with (open(output_file, "w", newline='')) as f:
        json.dump(fighter_data, f, indent=4)
        
def expected_odds(target_fighter_elo, opponent_elo, target_fighter_last_game_was_loss=False, opponent_last_game_was_loss=False, target_opponent_weight_ratio=0):
    elo_difference = target_fighter_elo - opponent_elo
    # test this variable later
    # LAST_GAME_WAS_LOST = 50
    
    # all else being equal, a fighter moving down 10% should have an 75% chance of winning
    WEIGHT_FACTOR = 10

    adjusted_elo_difference = elo_difference
    adjusted_elo_difference += (target_opponent_weight_ratio-1)*100 * WEIGHT_FACTOR
    # if target_fighter_last_game_was_loss: adjusted_elo_difference+=LAST_GAME_WAS_LOST
    # if opponent_last_game_was_loss: adjusted_elo_difference-=LAST_GAME_WAS_LOST

    return 1 / (1 + 10 ** (-(adjusted_elo_difference) / 400))

def elo_change(expected_odds, result, k_factor=32):
    return k_factor * (result - expected_odds)

if __name__ == "__main__":
    write_fighter_data(output_file="fighter_data.json")