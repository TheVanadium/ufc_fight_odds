# elo system for the fighter data

import csv

FIGHT_DATA_FILE = "chronological_total_fight_data.csv"
OUTPUT_FILE = "fighter_data.csv"

def write_fighter_data(fight_data_file=FIGHT_DATA_FILE, output_file=OUTPUT_FILE):
    fighter_data = {}
    with (open(FIGHT_DATA_FILE, "r")) as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)

        # fighter_name {
        # elo: 1500 (default)
        #   record: {
        #       date: 
        #           opponent:
        #           result:
        #       date: 
        #           opponent:
        #           result:
        #  }    etc.
        #   }
        # }
        
        DATE_INDEX = -4
        WINNER_INDEX = -1
        WEIGHT_CLASS_INDEX = -2

        for row in reader:
            # print fighter names, date, and winner
            for fighter in (row[0], row[1]):
                if fighter not in fighter_data:
                    fighter_data[fighter] = {
                        "elo": 1500,
                        "record": {}
                    }
            
            for fighter in (row[0], row[1]):
                fighter_data[fighter]["record"][row[DATE_INDEX]] = {}
                fighter_data[fighter]["record"][row[DATE_INDEX]]["opponent"] = row[1] if fighter == row[0] else row[0]
                
                result: int = 1
                if row[WINNER_INDEX] == fighter_data[fighter]["record"][row[DATE_INDEX]]["opponent"]:result = 0
                elif row[WINNER_INDEX] == "": result = 0.5
                fighter_data[fighter]["record"][row[DATE_INDEX]]["result"] = result

                current_elo = fighter_data[fighter]["elo"]
                opponent_name = fighter_data[fighter]["record"][row[DATE_INDEX]]["opponent"]
                opponent_elo = fighter_data[opponent_name]["elo"]

                current_fight_odds = expected_odds(current_elo, int(opponent_elo))
                # if fighter has had less than 3 fights, use a k-factor of 64
                k_factor = 32
                if len(fighter_data[fighter]["record"]) < 3: k_factor = 64
                fighter_data[fighter]["elo"] += elo_change(current_fight_odds, result, k_factor)

                if fighter == "Donald Cerrone": 
                    print(row[0], row[1], row[DATE_INDEX], row[WINNER_INDEX])
                    print(fighter_data[fighter_data[fighter]["record"][row[DATE_INDEX]]["opponent"]]["elo"])
                    print(fighter_data[fighter]["elo"])

    with (open(OUTPUT_FILE, "w", newline='')) as f:
        writer = csv.writer(f)
        writer.writerow(["fighter", "elo", "record"])
        for fighter in fighter_data:
            writer.writerow([fighter, fighter_data[fighter]["elo"], fighter_data[fighter]["record"]])


# expected odds
def expected_odds(target_fighter_elo, opponent_elo, target_fighter_last_game_was_loss=False, opponent_last_game_was_loss=False):
    elo_difference = target_fighter_elo - opponent_elo
    # test this variable later
    # LAST_GAME_WAS_LOST = 50
    adjusted_elo_difference = elo_difference
    # if target_fighter_last_game_was_loss: adjusted_elo_difference+=LAST_GAME_WAS_LOST
    # if opponent_last_game_was_loss: adjusted_elo_difference-=LAST_GAME_WAS_LOST
    
    return 1 / (1 + 10 ** (-(adjusted_elo_difference) / 400))

# elo change
def elo_change(expected_odds, result, k_factor=32):
    return k_factor * (result - expected_odds)

if __name__ == "__main__":
    write_fighter_data()