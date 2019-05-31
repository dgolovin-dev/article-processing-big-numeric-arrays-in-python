import os
import csv
from datetime import datetime

DATA_DIR='../data'
# this directory contains only 1 sample,
# make multiple copies of this sample for reasonable results

data = dict()
for root, dirs, files in os.walk(DATA_DIR):
    for filename in files:
        asset = filename.split('.')[0]
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            first = True
            series = []
            headers = None
            for row in csvreader:
                if first:
                    first = False
                    headers = row
                    continue
                row = [float(row[i]) if i > 0 else datetime.strptime(row[i], "%Y-%m-%d").date()
                       for i in range(len(row))]
                series.append(row)
            data[asset] = series

print("loaded")

# меряем память после загрузки массива данных
from memory_profiler import memory_usage
print(memory_usage())
