from p1_e4_load_xr_netcdf import data
from p2_e3_calc_ema_numba import calc_ema
import xarray as xr
import numpy as np

# нужно провести поправку на сплиты перед расчетом ema
split_cumprod = data.loc[:, 'split', :].cumprod('date')
data.loc[:, ['close', 'open', 'high', 'low', 'divs'], :] = data.loc[:, ['close', 'open', 'high', 'low', 'divs'], :] * split_cumprod
data.loc[:, 'vol', :] = data.loc[:, 'vol', :] / split_cumprod

#собственно расчет портфеля
close_ema = calc_ema(data.loc[:, 'close', :], 20)
liquidity_ema = calc_ema(data.loc[:, 'close', :] * data.loc[:, 'vol', :], 30)
portfolio = liquidity_ema.where(close_ema > 0).fillna(0)

# нормировка
portfolio_daily_sum = portfolio.sum('asset')
portfolio_daily_sum = portfolio_daily_sum.where(portfolio_daily_sum > 0).fillna(1)
portfolio = portfolio / portfolio_daily_sum

portfolio.to_netcdf('../portfolio.nc', compute=True)
# portfolio.transpose('date', 'asset').to_pandas().to_csv('portfolio.csv')

print("done")
