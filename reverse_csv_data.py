import csv

INPUT_FILE_NAME = "raw_total_fight_data.csv"
OUTPUT_FILE_NAME = "chronological_total_fight_data.csv"

def reverse_csv_data(file_name=INPUT_FILE_NAME):
    new_data = []
    header = []
    with (open(INPUT_FILE_NAME, "r")) as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        for row in reader:
            new_data.insert(0, row)

    with (open(OUTPUT_FILE_NAME, "w", newline='')) as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        for row in new_data:
            writer.writerow(row)
            
if __name__ == "__main__":
    reverse_csv_data()