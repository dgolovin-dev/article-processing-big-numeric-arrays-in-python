import os
import pandas as pd
import xarray as xr
import pickle

DATA_DIR='../data'
DATA2_DIR = '../data2'
NETCDF_FILE = '../data.nc'
PICKLE_FILE='../data.pickle'

data = []
for root, dirs, files in os.walk(DATA_DIR):
    for filename in files:
        #print("read", filename)
        asset = filename.split('.')[0]
        file_path = os.path.join(DATA_DIR, filename)
        series = pd.read_csv(file_path, sep=",", index_col="date")
        series = series.to_xarray().to_array('field')
        series.name = asset
        data.append(series)

data = xr.concat(data, pd.Index([d.name for d in data], name='asset'))

# write fields as separate csv files
os.makedirs(DATA2_DIR, exist_ok=True)
for f in data.field.values.tolist():
    print("write", f)
    ds = data.sel(field=f).transpose('date','asset').to_pandas()
    ds.to_csv(DATA2_DIR + "/" + f + '.csv',  float_format='%.2f')
