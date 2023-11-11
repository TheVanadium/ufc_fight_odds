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

`data-collector/` contains scripts and data for UFC fights from UFC 1 until UFC 294
### `additional_fight_scraper.py`
Scrapes Wikipedia for fight data and writes it to 4 json files (for speed):
- `fight_data_pre_2023-a.json`, `fight_data_pre_2023-b.json`, `fight_data_pre_2023-c.json`: Fight data for fights before 2023 in sorted in reverse chronological order.
- `fight_data_2023.json`: Fight data for fights in 2023 in sorted in reverse chronological order, with the latest fight being October 21, 2023 (because that was the most recent at the time the data was scraped).
