import xarray as xr
import pickle

data = pickle.load(open("../data.pickle", 'rb'))

# measure memory after loading
# measure memory after loading
import gc
from memory_profiler import memory_usage
gc.collect()
print("current memory:", memory_usage()[0]*1024, "Kb")
