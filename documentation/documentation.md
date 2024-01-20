# UFC Fight Prediction Generator
In Progress

## Purpose
To generate strong and accurate predictions for UFC fights based on the fighters' previous fights (because I'm cheap and don't want to pay for a UFC fight API)
Approximate "Fight Elo" of sorts for UFC fighters

Input: Two fighters' names <br>
Output: A prediction of the winner and the probability of that fighter winning

### Architecture

1. Scraped Wikipedia for fight data via ```fight_scraper.py```
2. Sorted fight data into fighter data via ```write_training_fighter_data.py```<br>
<i>The following is in progress:</i>
3. Train a model to predict the winner of a fight based on the fighters' previous fights
4. Create a web app to display the predictions

### Related Projects
What makes this project distinct is that it uses an elo system based on fighters' records to predict the outcome of fights, as well as percentage odds for the result. This system ignores fighting statistics such as striking and takedown accuracy. This project will try to optimize the odds calculation using brier scores and standard deviation.

#### "Ranking MMA fighters using the Elo rating system" by Leonardo Pinheiro: https://medium.com/geekculture/ranking-mma-fighters-using-the-elo-rating-system-2704adbf0c94
This project used an elo ranking system for fighters, but did not use it to predict fights. It also does not try optimizing to find the ideal k-factor for fight elo.

#### "UFC MMA Predictor" by Jason Chan: https://github.com/jasonchanhku/UFC-MMA-Predictor
This project predicts odds for UFC fights based on fighter's fighting statistics and betting odds. This project will attempt to predict odds based on previous fights, not betting odds or statistics.

## Admin Scripts
Scripts that are used to manage the data for the app.

`fight-data-collector/` <br>
Contains collection scripts and data for UFC fights from UFC 1 until UFC 294
- `fight_scraper.py` Scrapes Wikipedia for fight data and writes it to 4 json files (for speed), below:
- `fight_data_pre_2023-a.json`, `fight_data_pre_2023-b.json`, `fight_data_pre_2023-c.json`: Fight data for fights before 2023 in sorted in reverse chronological order.
- `fight_data_2023.json`: Fight data for fights in 2023 in sorted in reverse chronological order, with the latest fight being October 21, 2023 (because that was the most recent at the time the data was scraped).

Fight data format: <br>
    Template
    
    "MMM DD, YYYY(#)": {
        "Fight: Fighter 1 vs Fighter 2": {
            "winner": "Fighter 1",
            "loser": "Fighter 2",
            "weight_class": "Weight Class",
            "draw": false,
            "no_contest": false,
            "championship_fight": false
        },
        "Fight: Fighter 3 vs Fighter 4": {
            "winner": "Fighter 3",
            "loser": "Fighter 4",
            "weight_class": "Weight Class",
            "draw": false,
            "no_contest": false,
            "championship_fight": false
        },
        ...
    },
<br>Example

    "Jul 22, 2017": {
            "Fight: Chris Weidman vs Kelvin Gastelum": {
            "winner": "Chris Weidman",
            "loser": "Kelvin Gastelum",
            "weight_class": "Middleweight",
            "draw": false,
            "no_contest": false,
            "championship_fight": false
        },
            "Fight: Darren Elkins vs Dennis Bermudez": {
            "winner": "Darren Elkins",
            "loser": "Dennis Bermudez",
            "weight_class": "Featherweight",
            "draw": false,
            "no_contest": false,
            "championship_fight": false
        },
    }
    ...

`fight_adder.py`<br>
Contains the function `add_fight`, which takes a fighter data dictionary as an input (formatted the same way as `training_fighter_data.json`) and adds the fight to the fighter's record in the input dictionary. There is no return type; editing is done in-place.

`fight_prediction_generator`<br>
Still under construction
Contains the function `write_fight_predictions` which uses the fighter data file (`training_fighter_data.json`) to generate fight odds for 2023 matches. The function (should) not only predict fight odds based on old data, but after the fight is over, it will update the fighter data (in a temporary file) with the correct data for more predictions.

`odds_calculation_methods.py`<br>
Contains functions for calculating the odds of a fighter winning a match based on elo and other parameters

`training_fighter_data.json`<br>
Contains data for each fighter until 2023 in the following format:<br>

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
-"Weight Class" does not have spaces and is capitalized (for example, "Women's Flyweight" would be "Women'sFlyweight"). There was an issue with scraping that made it so that there would be spaces after weight classes and in between words and whatnot (for example, "Flyweight " instead of "Flyweight"), so this is a quick fix. If it turns out there is no problem after all, this can be removed.

`write_training_fighter_data.py`<br>
Contains the function `write_training_fighter_data.py`, which goes through all 3 pre-2023 fight data files and uses `add_fight` (see `fight_adder.py`) to generate a dictionary containing all the fighters then adds all the fights to the fighter data file (`training_fighter_data.json`).
This data will be the training data for the prediction model. The testing data will be 2023 fights, onwards.

#### Tests
Tests are located in the `tests` directory.

`test_fight_adder.py`<br>
Tests the `add_fight` function in `fight_adder.py`.