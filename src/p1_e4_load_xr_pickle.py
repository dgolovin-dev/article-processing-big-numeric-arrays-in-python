import xarray as xr
import pickle

data = pickle.load(open("../data.pickle", 'rb'))

print("loaded")

print(data)
# measure memory after loading
from memory_profiler import memory_usage
print(memory_usage())
