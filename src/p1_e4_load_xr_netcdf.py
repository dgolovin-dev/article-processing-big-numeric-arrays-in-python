import xarray as xr

data = xr.open_dataarray('../data.nc', decode_times=True).compute()

print("loaded")

# measure memory after loading
from memory_profiler import memory_usage
print(memory_usage())
