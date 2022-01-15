import xarray as xr
import time

import cema

data = xr.open_dataarray('../data.nc', decode_times=True).compute()

def cython_ema(data, n):
    nparr = data.values
    nparr = cema.c_ema(nparr, n)
    return xr.DataArray(nparr, dims=[ 'asset', 'date'], coords={'date': data.date, 'asset': data.asset})

t0 = time.time()
ema = xr.zeros_like(data)
for f in data.field.values.tolist():
    ema.loc[:,f,:] = cython_ema(data.loc[:, f, :], 20)
t1 = time.time()
print('time:', t1 - t0)

