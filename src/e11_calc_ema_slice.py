import xarray as xr
import numpy as np
import time

data = xr.open_dataarray('../data.nc', decode_times=True).compute()

def calc_ema(data, n):
    k = 2.0 / (1 + n)
    _k = 1 - k
    ema = xr.zeros_like(data)
    prev_ema = xr.zeros_like(ema.isel(date=0))
    for t in data.coords['date']:
        cur_data = data.loc[:, t]
        cur_finite = np.isfinite(cur_data)
        prev_finite = np.isfinite(prev_ema)

        ema.loc[:, t] = cur_data
        ema.loc[prev_finite, t] = prev_ema.loc[prev_finite]
        cur_prev_finite = np.logical_and(prev_finite, cur_finite)
        ema.loc[cur_prev_finite, t] = (k * cur_data + _k * prev_ema).loc[cur_prev_finite]

        prev_ema = ema.loc[:, t]
    return ema

t0 = time.time()
ema = xr.zeros_like(data)
for f in data.field.values.tolist():
    ema.loc[:,f,:] = calc_ema(data.loc[:,f,:], 20)
t1 = time.time()
print('time:', t1 - t0)
