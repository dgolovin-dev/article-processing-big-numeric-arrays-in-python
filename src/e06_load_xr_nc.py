import xarray as xr

data = xr.open_dataarray('../data.nc', decode_times=True).compute()

# measure memory after loading
import gc
from memory_profiler import memory_usage
gc.collect()
print("current memory:", memory_usage()[0]*1024, "Kb")
