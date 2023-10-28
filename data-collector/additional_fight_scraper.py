import csv
import json
import requests
from bs4 import BeautifulSoup

INDEX_OF_MOST_RECENT_FIGHT = 668
INDEX_OF_EARLIEST_FIGHT_IN_2023 = 632
UFC_EVENTS_LIST_LINK = "https://en.wikipedia.org/wiki/List_of_UFC_events"

# "first" and "last" are inclusive and chronological; but the data starts with the first chronological fight and ends with the last chronological fight
def scrape_ufc_events(first_fight_index: int, last_fight_index: int, file="test_remaining_ufc_fights.json"):
    ufc_event_links: dict = {}
    # go to website
    # table<-id="Past_events"
    # in tbody, go through each tr 
        # in each tr, 1st td is event number
        # 2nd td contains an a with href (only the directory, will need to prepend wikipedia.org)
        # 3rd td contains date
    # key: date, value: event number

    response = requests.get(UFC_EVENTS_LIST_LINK)
    soup = BeautifulSoup(response.text, "lxml")

    past_events_table = soup.find("table", id="Past_events")
    past_events_table_body = past_events_table.find("tbody")
    past_events_table_rows = past_events_table_body.find_all("tr")
    # add 1 because of the header row
    row_number = INDEX_OF_MOST_RECENT_FIGHT + 1
    for row in past_events_table_rows:
        row_number -= 1
        if row_number > last_fight_index: continue
        if row.find("td") == None: continue
        if row.find("td").text.strip() == "—": continue
        event_number = int(row.find("td").text.strip())
        event_link = row.find("td").find_next_sibling("td").find("a")["href"]
        event_date = row.find("td").find_next_sibling("td").find_next_sibling("td").text.strip()

        ufc_event_links[event_date] = event_link
        if event_number == first_fight_index: break

    print (f"Number of events: {len(ufc_event_links)}")

    ufc_event_fights: dict = {}
    for date, link in ufc_event_links.items():
        print (f"Date: {date}")
        response_event_site = response = requests.get("https://en.wikipedia.org" + link)
        soup_event_site = BeautifulSoup(response_event_site.text, "lxml")

        results_header = soup_event_site.find("span", id="Results").parent
        results_table = results_header.find_next_sibling("table")
        fight_rows = results_table.find_all("tr")

        WINNER_ITEM_INDEX = 1
        LOSER_ITEM_INDEX = 3
        METHOD_ITEM_INDEX = 4

        for fight_row in fight_rows:
            if fight_row.find("th") != None: continue
            current_weight_class = fight_row.find_all("td")[0].text
            winner = fight_row.find_all("td")[WINNER_ITEM_INDEX].text
            loser = fight_row.find_all("td")[LOSER_ITEM_INDEX].text
            draw = fight_row.find_all("td")[METHOD_ITEM_INDEX].text.startswith("Draw")
            no_contest = fight_row.find_all("td")[METHOD_ITEM_INDEX].text.startswith("No Contest")
            championship_fight = "(c)" in winner or "(c)" in loser

            replace_characters = {
                "\n": "",
                " (c)": "",
                " (ic)": ""
            }
            for character in replace_characters:
                winner = winner.replace(character, "")
                loser = loser.replace(character, "")
                current_weight_class = current_weight_class.replace(character, "")

            fight_name = f"Fight: {winner} vs {loser}"
            print(fight_name)
            if not date in ufc_event_fights: ufc_event_fights[date] = {}
            ufc_event_fights[date][fight_name] = {
                "winner": winner,
                "loser": loser,
                "weight_class": current_weight_class,
                "draw": draw,
                "no_contest": no_contest,
                "championship_fight": championship_fight
            }
    with open(file, "w") as f:
        json.dump(ufc_event_fights, f)            

if __name__ == "__main__":
    # scrape_ufc_events(INDEX_OF_EARLIEST_FIGHT_IN_2023, INDEX_OF_MOST_RECENT_FIGHT, file="fight_data_2023.json")
    scrape_ufc_events(1, INDEX_OF_EARLIEST_FIGHT_IN_2023-1, file="fight_data_pre_2023.json")