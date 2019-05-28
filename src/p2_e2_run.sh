#!/usr/bin/env bash

echo "Part #2 example #2: calc ema slice"
/usr/bin/time -f "%E %MKb" python3 p2_e2_calc_ema_slice.py > ../report/p2_e2.txt 2>&1
