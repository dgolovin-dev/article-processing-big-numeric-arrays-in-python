from p1_e4_load_xr_netcdf import data
import xarray as xr
import numpy as np
import time

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

if __name__ == '__main__':
    t0 = time.time()
    ema = xr.zeros_like(data.loc[:,'close',:])
    ema.values = calc_ema_np(data.loc[:, 'close', :].values, 20)
    t1 = time.time()

    print('done', t1 - t0, ema)
