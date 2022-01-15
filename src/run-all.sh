#!/usr/bin/env bash

TIMEOUT="300s"
ENV=bigarray
PREPARE=1

mkdir -p ../report


if [ $PREPARE -eq 1 ]; then
echo "..."
echo "Create env and install dependencies..."
conda create -n "$ENV" -y \
importlib-metadata=4.8 \
pandas=1.3 \
xarray=0.20 \
memory_profiler=0.58 \
scipy=1.7.3 \
cython=0.29 \
python=3.7 \
numba=0.53 \
numpy=1.20
fi


echo "Activate env..."
source "$(dirname $CONDA_EXE)/../etc/profile.d/conda.sh"
conda activate "$ENV"

if [ $PREPARE -eq 1 ]; then

echo "Compile cyton"
cython -3 cema.pyx
gcc -shared -pthread -fPIC -fwrapv -Wall -O2 \
-I "$CONDA_PREFIX/lib/python3.6/site-packages/numpy/core/include/" \
-I "$CONDA_PREFIX/include/python3.7m/" \
-o cema.so cema.c

echo "..."
echo "Generate data..."
python e00_generate_test_data.py

echo "..."
echo "Group data by column..."
python e03_group_by_column.py

echo "..."
echo "Merge data into 1 file..."
python e05_convert_to_nc_and_pickle.py

fi

echo "..."
echo "Clear FS cache"
sudo bash -c "sync; echo 3 > /proc/sys/vm/drop_caches"

echo "..."
echo "Load data (pure Python)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e01_load_pure_python.py \
2>&1 | tee ../report/e01_load_pure_python.txt

echo "..."
echo "Load data (Pandas)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e02_load_pandas.py 2>&1 \
| tee ../report/e02_load_pandas.txt

echo "..."
echo "Load data (Pandas 7)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e04_load_pandas_7.py 2>&1 \
| tee ../report/e04_load_pandas_7.txt

echo "..."
echo "Load data (xarray netcdf)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" python e06_load_xr_nc.py \
2>&1 | tee ../report/e06_load_xr_nc.txt

echo "..."
echo "Load data (xarray pickle)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" python e07_load_xr_pickle.py \
2>&1 | tee ../report/e07_load_xr_pickle.txt

echo "..."
echo "Calc ema (naive)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" python e08_calc_ema_naive.py \
2>&1 | tee ../report/e08_calc_ema_naive.txt

echo "..."
echo "Calc ema (naive improved)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e10_calc_ema_naive_improved.py \
2>&1 | tee ../report/e10_calc_ema_naive_improved.txt

echo "..."
echo "Calc ema (numpy)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e09_calc_ema_numpy.py \
2>&1 | tee ../report/e09_calc_ema_numpy.txt

echo "..."
echo "Calc ema (slice)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e11_calc_ema_slice.py \
2>&1 | tee ../report/e11_calc_ema_slice.txt

echo "..."
echo "Calc ema (slice numpy)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e12_calc_ema_slice_numpy.py \
2>&1 | tee ../report/e12_calc_ema_slice_numpy.txt

echo "..."
echo "Calc ema (cython)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e13_calc_ema_cython.py \
2>&1 | tee ../report/e13_calc_ema_cython.txt

echo "..."
echo "Calc ema (numba)"
/usr/bin/time -f "time: %E peak memory: %MKb" \
timeout "$TIMEOUT" \
python e14_calc_ema_numba.py \
2>&1 | tee ../report/e14_calc_ema_numba.txt
