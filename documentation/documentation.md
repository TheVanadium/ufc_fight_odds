# UFC Fight Prediction Generator
In Progress

## Purpose
To generate strong and accurate predictions for UFC fights based on the fighters' previous fights (because I'm cheap and don't want to pay for a UFC fight API)

Input: Two fighters' names
Output: A prediction of the winner and the probability of that fighter winning

### Architecture

1. Scraped Wikipedia for fight data via ```additional_fight_scraper.py```
2. Sorted fight data into fighter data via ```write_training_fighter_data.py```
Currently in the works:
3. Train a model to predict the winner of a fight based on the fighters' previous fights
4. Create a web app to display the predictions

## Admin Scripts
Scripts that are used to manage the data for the app.

`fight-data-collector/` contains scripts and data for UFC fights from UFC 1 until UFC 294
### `additional_fight_scraper.py`
Scrapes Wikipedia for fight data and writes it to 4 json files (for speed):
- `fight_data_pre_2023-a.json`, `fight_data_pre_2023-b.json`, `fight_data_pre_2023-c.json`: Fight data for fights before 2023 in sorted in reverse chronological order.
- `fight_data_2023.json`: Fight data for fights in 2023 in sorted in reverse chronological order, with the latest fight being October 21, 2023 (because that was the most recent at the time the data was scraped).

`fight_adder.py`
Contains the function `add_fight`, which takes fighter data as an input and adds the fight to the fighter's record in the appropriate json file (the officially correct data is in `fighter_data.json`).
Because generating every fight takes a while to process and is prone to errors (see `write_training_fighter_data.py`), fight additions are logged in `action_log.txt`.

`fight_prediction_generator`
Still under construction
Contains the function `write_fight_predictions` which uses the fighter data file (`fighter_data.json`) to generate fight odds for 2023 matches. The function (should) not only predict fight odds based on old data, but after the fight is over, it will update the fighter data (in a temporary file) with the correct data for more predictions.

`fighter_data.json`
Contains data for each fighter until 2023 in the following format:
"Fighter name": {
        "elo": XXXX.XXXXXX,
        "record": {
            "MMM DD, YYYY(#)": {
                "opponent": "Opponent Name",
                "result": result#,
                "weight_class": "Weight Class"
            },
            ...
        }
    },
    ...
"elo" is a float representing the fighter's general fighting skill (higher elo indicates higher skill)
"record" is a dictionary of the fighter's fights, sorted in chronological order
-In the date key, the month is abbreviated to 3 letters (Jan, Feb, Mar, etc.), the day can be 1 or 2 digits, and the year is 4 digits, potentially with an additional number after it representing the index (zero-indexed) of the fight in the day (for example, Nov 12, 19931 would represent that fighter's 2nd fight on Nov 12)
-result# is 1 for a win, 0.5 for a draw, and 0 for a loss

`odds_calculation_methods.py`
Contains functions for calculating the odds of a fighter winning a match based on elo and other parameters
-`expected_odds` takes in a target fighter and their opponent and returns the odds of the target fighter winning
-`elo_change` takes in a fighter's odds of victory and the result of a match and returns the appropriate amount to change the fighter's elo by

`write_training_fighter_data.py`
Contains the function `write_training_fighter_data.py`, which goes through all 3 pre-2023 fight data files and uses `add_fight` (see `fight_adder.py`) to add all the fights to the fighter data file (`fighter_data.json`).
Notably, this takes quite a long time (several minutes) to finish.

#### Tests
`test_fight_adder.py`
Tests the `add_fight` function in `fight_adder.py` by adding a fight to a test fighter's record and checking if the result is correct. The changes are made to `test_fighter_data.json` after `fighter_data.json`'s data is copied into it. 