from p1_e4_load_xr_netcdf import data
import xarray as xr
import numpy as np
from numba import jit
import time

#@jit
def numba_ema(data, n):
    k = 2.0 / (1 + n)
    _k = 1 - k
    ema = np.zeros(data.shape, np.float64)
    for a in range(data.shape[0]):
        pe = np.nan
        for t in range(data.shape[1]):
            e = data[a, t]
            if not np.isnan(pe):
                if np.isnan(e):
                    e = pe
                else:
                    e = k * e + _k * pe
            ema[a, t] = e
            pe = e
    return ema


def calc_ema(data, n):
    nparr = data.values
    nparr = numba_ema(nparr, n)
    return xr.DataArray(nparr, dims=['asset', 'date'],coords={'date': data.coords['date'], 'asset': data.coords['asset']})

if __name__ == '__main__':
    t0 = time.time()
    ema = calc_ema(data.loc[:, 'close', :], 20)
    t1 = time.time()
    # ema = calc_ema(data.loc[:, 'close', :], 20)
    # t2 = time.time()
    print('done', t1 - t0) #, t2 - t1)
    #print(ema)
