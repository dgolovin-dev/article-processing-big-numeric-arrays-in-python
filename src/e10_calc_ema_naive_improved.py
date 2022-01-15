import xarray as xr
import numpy as np
import time

data = xr.open_dataarray('../data.nc', decode_times=True).compute()

def calc_ema_list(prices, n):
    k = 2.0 / (1 + n)
    _k = 1 - k
    ema = []
    pe = np.nan
    for e in prices:
        if not np.isnan(pe):
            if np.isnan(e):
                e = pe
            else:
                e = k * e + _k * pe
        ema.append(e)
        pe = e
    return ema

ema = xr.zeros_like(data)

t0 = time.time()
for a in data.asset.values.tolist():
    for f in data.field.values.tolist():
        ema.loc[a,f] = calc_ema_list(data.loc[a,f].values.tolist(), 20)
t1 = time.time()

print('time:', t1-t0)
