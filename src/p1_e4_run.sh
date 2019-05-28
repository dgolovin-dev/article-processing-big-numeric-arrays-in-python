#!/usr/bin/env bash

echo "Part #1 example #4: load data with xarray from netcdf"
/usr/bin/time -f "%E %MKb" python3 p1_e4_load_xr_netcdf.py > ../report/p1_e4.txt 2>&1
