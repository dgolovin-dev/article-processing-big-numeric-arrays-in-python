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

close_prices = data.loc[:, 'close', :]
ema = xr.zeros_like(close_prices)

t0 = time.time()
for a in close_prices.asset.values.tolist():
    ema.loc[a] = calc_ema_list(close_prices.loc[a].values.tolist(), 20)
t1 = time.time()

print('done', t1-t0)
