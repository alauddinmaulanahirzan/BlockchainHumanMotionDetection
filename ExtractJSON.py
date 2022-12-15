import json
import csv
from Blockchain import *
import os

def extractJSON():
    file = open("iot-db-dump.json","r")
    data = json.load(file)
    counter = 0
    data_rows = []

    for machine in data.keys():
        counter += 1
        message = f">>'{machine}'"
        blocks = data[machine]
        # Iterate per Block
        for block in blocks.keys():
            block_previous = blocks[block]["01 Previous"]
            block_data = Blockchain.decryptMessage(blocks[block]["02 Data"]["0-0 Data"])
            block_hash = blocks[block]["03 Hash"]

            # Insert into Row
            row = []
            row.append(counter)
            row.append(machine)
            row.append(block)
            row.append(block_previous)
            row.append(block_data)
            row.append(block_hash)
            data_rows.append(row)

    # Write to CSV
    filename = "data-dump.csv"
    if os.path.isfile(filename):
        os.remove(filename)
    # Set Header CSV
    header = ["No","Machine","Block","Previous","Data","Hash"]
    with open(filename,"w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for input_row in data_rows:
            writer.writerow(input_row)

def main():
    extractJSON()

if __name__ == '__main__':
    main()
