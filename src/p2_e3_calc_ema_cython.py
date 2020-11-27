# cython -3 cema.pyx
# gcc -shared -pthread  -fPIC -fwrapv -Wall -O2 \
# -I /opt/anaconda/envs/.../lib/python3.7/site-packages/numpy/core/include/ \
# -I  /opt/anaconda/envs/.../include/python3.7m/ -o cema.so cema.c

import xarray as xr
import time

import cema

def cython_ema(data, n):
    nparr = data.values
    nparr = cema.c_ema(nparr, n)
    return xr.DataArray(nparr, dims=[ 'asset', 'date'], coords={'date': data.date, 'asset': data.asset})

data = xr.open_dataarray('../data.nc', decode_times=True).compute()
t0 = time.time()
ema = cython_ema(data.loc[:, 'close', :], 20)
t1 = time.time()
print('done', t1 - t0)
print(ema)


