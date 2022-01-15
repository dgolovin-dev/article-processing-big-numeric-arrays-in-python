import os
import pandas as pd

DATA_DIR='../data'

data = dict()
for root, dirs, files in os.walk(DATA_DIR):
    for filename in files:
        asset = filename.split('.')[0]
        file_path = os.path.join(DATA_DIR, filename)
        series = pd.read_csv(file_path, sep=",", index_col="date")
        data[asset] = series

print("loaded")

# measure memory after loading
import gc
from memory_profiler import memory_usage
gc.collect()
print("current memory:", memory_usage()[0]*1024, "Kb")
