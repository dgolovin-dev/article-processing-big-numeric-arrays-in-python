import xarray as xr
import numpy as np
import time

data = xr.open_dataarray('../data.nc', decode_times=True).compute()


def calc_ema_np(data, n):
    k = 2.0 / (1 + n)
    _k = 1 - k
    ema = np.zeros_like(data)
    prev_ema = np.zeros_like(ema[:,0])
    for t in range(data.shape[1]):
        cur_data = data[:, t]
        cur_finite = np.isfinite(cur_data)
        prev_finite = np.isfinite(prev_ema)
        ema[:, t] = cur_data
        ema[prev_finite, t] = prev_ema[prev_finite]
        cur_prev_finite = np.logical_and(prev_finite, cur_finite)
        ema[cur_prev_finite, t] = (k * cur_data + _k * prev_ema)[cur_prev_finite]
        prev_ema = ema[:, t]
    return ema


t0 = time.time()
ema = xr.zeros_like(data)
for f in data.field.values.tolist():
    ema.loc[:,f,:].values = calc_ema_np(data.loc[:,f,:].values, 20)
t1 = time.time()

print('time:', t1 - t0)
