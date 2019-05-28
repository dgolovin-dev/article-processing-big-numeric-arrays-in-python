#!/usr/bin/env bash

echo "Part #1 example #1: load data from csv"
/usr/bin/time -f "%E %MKb" python3 p1_e1_load.py > ../report/p1_e1.txt 2>&1
