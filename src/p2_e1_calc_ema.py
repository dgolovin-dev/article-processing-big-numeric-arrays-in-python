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
    for a in data.coords['asset']:
        pe = np.nan
        for t in data.coords['date']:
            e = data.loc[a, t]
            if not np.isnan(pe):
                if np.isnan(e):
                    e = pe
                else:
                    e = k * e + _k * pe
            ema.loc[a, t] = e
            pe = e
    return ema

if __name__ == '__main__':
    ema = calc_ema(data.loc[:, 'close', :], 20)
    print('done')
