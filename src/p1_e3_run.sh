#!/usr/bin/env bash

echo "Part #1 example #3: convert data from csv to netcdf"
/usr/bin/time -f "%E %MKb" python3 p1_e3_convert_to_nc.py > ../report/p1_e3.txt 2>&1
