from p1_e4_load_xr_netcdf import data
import xarray as xr
import numpy as np

def calc_ema(data, n):
    k = 2.0 / (1 + n)
    _k = 1 - k
    ema = xr.DataArray(
        np.zeros([len(data.coords['asset']), len(data.coords['date'])], np.float64),
        dims=['asset', 'date'],
        coords={'date': data.coords['date'], 'asset': data.coords['asset']}
    )
    prev_ema = xr.DataArray(
        np.full([len(data.coords['asset'])], np.nan, dtype=np.float64),
        dims=['asset'],
        coords={'asset': data.coords['asset']}
    )
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

if __name__ == '__main__':
    ema = calc_ema(data.loc[:, 'close', :], 20)
    print('done')
