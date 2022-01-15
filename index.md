# Processing big numeric arrays in python

## Intro

Hello. 

As you know, Python is an interpreted language and it is not very fast at processing data. C, Java or any other compilable language is much faster. However, Python is very popular among data scientists and they use it for processing data. But if you want to reach acceptable performance you **MUST** use some *special libraries* which allow you to use the performance benefits of compiled languages.

In this article I will talk about *numpy*, *pandas*, *xarray*, *cython*, *numba*. And I will show you a real example of how to use them properly and boost the performance hundreds of times. The source code of the example is available on github, so you can download and check them by yourself.


## Task

**Definition**: *Calculate [Exponential Moving Averages](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average)
for all columns of 2000 stocks 20-years daily data series.*

## Summary
I will give you the benchmark results in advance.
See them and then decide if you want to read this whole article or not.

| **Approach**            | **time**      | **peak RAM** | **end RAM** |
|-------------------------|---------------|--------------|-------------|
| **Load data**           |               |              |             |
| pure python (csv)       | **1m37s**     | 4GB          | **4GB**     |
| pandas (csv)            | **12s**       | 1.4GB        | **1.4GB**   |
| pandas (csv, big files) | **8s**        | 0.72GB       | **0.72GB**  |
| xarray (netcdf, 1 file) | **1.6s**      | 1.2GB        | **0.65GB**  |
| xarray (pickle, 1 file) | **1.3s**      | 1.2GB        | **0.65GB**  |
| **Calculate EMA**       |               |              |             |
| naive                   | **>5m**       | 1.2GB        | 1.2GB       |
| naive numpy             | **3m**        | 1.2GB        | 1.2GB       |
| naive improved          | **2m**        | 1.2GB        | 1.2GB       |
| slices                  | **4m**        | 1.2GB        | 1.2GB       |
| numpy slices            | **2.4s**      | 1.2GB        | 1.2GB       |
| cython                  | **0.5s**      | 1.2GB        | 1.2GB       |
| numba                   | **0.5s(+0.3s)** | 1.2GB        | 1.2GB       |

## Task - additional info

**Data sample**:
```txt
date,open,high,low,close,vol,divs,split
1998-01-01,2,3,1,2,23232,0.1,1
1998-01-02,2,3,1,3,32423,0,2
...
```

**Restrictions**: 
- *execution time should be less than 10 seconds*
- *your program should consume less than 1.5GB RAM*

This task looks simple, but the volume of the data and the restrictions make this task not so easy.

## Measures
*Shortly about how I measure consumed RAM and execution time.*

In order to evaluate the approaches, I will use this command to measure the peak memory and the execution time:
```bash
/usr/bin/time -f "time: %E peak memory: %MKb" ...
```
Also, I am going to use `timeout` command to limit the execution time because sometimes it can take hours.
```bash
timeout "300s" ...
```
Additionaly, before loading the data, I will clear the FS cache:
```bash
sudo bash -c "sync; echo 3 > /proc/sys/vm/drop_caches"
```
After loading the data, I am going to measure the current memory consumption 
with `memory_profiler`:
```python
import gc
from memory_profiler import memory_usage
gc.collect()
print("current memory:", memory_usage()[0]*1024, "Kb")
```

When I calculate ema, I will use the `time` module to measure the execution time 
excluding the loading time:
```python
import time

t0 = time.time()
...
print('time:', t1 - t0)
```

## Generate the data 

This script generates 2000 series. 
```bash
$ python e01_generate_test_data.py
```
[source code](src/generate_test_data.py)

Notice, that size of these series is about **0.5GB**. 
(You can generate more, but this amount is enough to demonstrate all the ideas.)

## Load data to RAM

First, we need to load the data.
We'll try different approaches, and I'll show you how to reorganize your data and significantly reduce the time and RAM.

**Load with pure Python (csv)**

First, let's do it with pure Python.

Code:
```python
{% include_relative src/e01_load_pure_python.py  %}
```

Report:

```txt
{% include_relative report/e01_load_pure_python.txt  %}
```
The execution time is **1m38s** and the consumed memory is about **4GB**.
This is unacceptable. Let's try the other approaches.

### Load with Pandas (csv)

Next, we will use pandas to load the data.

Code:
```python
{% include_relative src/e02_load_pandas.py  %}
```

Report:

```txt
{% include_relative report/e02_load_pandas.txt  %}
```

The execution time is **12s** and the consumed memory is about **1.4GB**.

This is much faster, but it still slow. 

And, as you see, pandas consumes much less memory than pure Puthon. 
The reason is that pandas uses internally numpy arrays which based on C-arrays.
C-arrays are much more efficient to store numbers than python lists.
But the data is still about 3 times larger in RAM than on HDD
because pandas creates separate indexes for each file.
It makes sense to reorganize the data to reduce the number of files.

**Load with pandas (csv, big files)**

The data in these files contain the same columns, so we can load all these data and 
save the every column data for all assets in the separate file.

```bash
$ python e03_group_by_column.py
```
[source code](src/e03_group_by_column.py)

Well, let's try to load the reorganized data and compare the results:

Code:
```python
{% include_relative src/e04_load_pandas_7.py  %}
```

Report:

```txt
{% include_relative report/e04_load_pandas_7.txt  %}
```

The execution time is **8s** and the consumed memory is about **0.72GB**.

*You can considerably improve the performance if you switch from CSV(text format) 
to any another binary format(netcdf, pickle, etc).*

**Load with xarray (netcdf, pickle)**

Unfortunately, pandas can work only with 2 dimensions. 
But `xarray`(similar library) can work with more than 2 dimensions, so we can join all data to one file.
Also it supports the netcdf binary file format (out of box with scipy).
We also test the pickle file format.

This script joins all the data to one file and saves it to netcdf and pickle.
```bash
$ python e05_convert_to_nc_and_pickle.py
```
[source code](src/e05_convert_to_nc_and_pickle.py)

Then we will load the data with netcdf and pickle:

**netcdf**
Code:
```python
{% include_relative src/e06_load_xr_nc.py  %}
```

Report:
```txt
{% include_relative report/e06_load_xr_nc.txt  %}
```

Result: **1.7s**, RAM **0.65GB**, peak ram **1.2GB**

**pickle**
Code:
```python
{% include_relative src/e07_load_xr_pickle.py  %}
```

Report:
```txt
{% include_relative report/e07_load_xr_pickle.txt  %}
```
Result: **1.3s**, RAM **0.65GB**, peak ram **1.2GB**

 
As you see the execution time is less than 2s, the difference is about 0.4s. 
Also, it consumes more peak memory than pandas in the previous case. 
It is ok if we take into consideration the further calculations.

If the results are almost equal, I advise you to use netcdf instead of pickle.
Pickle is connected very closely to the versions of libraries, 
so when you update your libraries the data can become unreadable from your code. 
This is a real headache, try to avoid that.

*Honestly, the performance of pandas may be the same if you use binary formats, 
but it a bit easier to start with xarray+netcdf at this time.*

## Load data - Conclusions

- use the right librarries (numpy,pandas,xarrray) for numeric data
- reduce number of files, join small files to big ones
- use binary data formats

## Calculate ema

**EMA naive**

At first let's try the naive approach.

Code:
```python
{% include_relative src/e08_calc_ema_naive.py  %}
```

Report:
```txt
{% include_relative report/e08_calc_ema_naive.txt  %}
```

The execution timed out (took more than 5min).

**EMA naive numpy**

When you read the documentation about xarray, you find that xarray is based on `numpy`.
You can think that it is a good idea to work with the data directly in numpy.

Let's try this.


Code:
```python
{% include_relative src/e09_calc_ema_numpy.py  %}
```

Report:
```txt
{% include_relative report/e09_calc_ema_numpy.txt  %}
```
The time is about **3min**. Better, but still slow.

**EMA naive improved**

The main problem is that we read and write the data element by element.
xarray(numpy and pandas too) uses system calls to external libraries
in order to access to the internal C-array(python can't work directly).
These calls are slow. We should use batching to reduce the number of calls.

The simplest approach is to extract the whole series from the C-array to python list,
calculate EMA and write the series back. Let's check.


Code:
```python
{% include_relative src/e10_calc_ema_naive_improved.py  %}
```

Report:
```txt
{% include_relative report/e10_calc_ema_naive_improved.txt  %}
```

The time is about **2min**. Slow.

**EMA with slices**
Another approach is work with the slices of elements and boolean masks.
It is also reduces the execution time.

Code:
```python
{% include_relative src/e11_calc_ema_slice.py  %}
```

Report:
```txt
{% include_relative report/e11_calc_ema_slice.txt  %}
```

The execution time is about **4min**. Bad. You can think that this is a wrong way,
But slice operations are very fast in numpy. 
So, You should bypass xarray and work with numpy directly 
if you want to reach good performance.

**EMA with numpy slices**
 
In this approach we are working with numpy slices directly.

Code:
```python
{% include_relative src/e12_calc_ema_slice_numpy.py  %}
```

Report:
```txt
{% include_relative report/e12_calc_ema_slice_numpy.txt  %}
```

The result is **3s**. This is great! We can say, that we solved the task.

Further, I will show some ways how to do it even faster.
We compile the code to work directly with C-arrays.
It is more complicated, but sometimes it is necessary.

**EMA with cython**

Let's try to use cython to make our code faster.

Cython - is a python-like language which may be converted to C,
compiled and linked to python.

This ema function implemented in cython:

Cython code:
```cython
{% include_relative src/cema.pyx  %}
```

As you, it is python-like, but it is not python.
There are a lot of code which specifies types and conversions. 
If you make even a minor mistake, your code may start to work 10 times slower 
or stop working at all.

For example the line 17. This line may look excess, 
but this is a some magic with types. 
We force it to use internal memory structure. 
Without this line the code works 14 times slower.

Also you have to convert and compile the code:
```bash
# convert to C
cython -3 cema.pyx
# compile
gcc -shared -pthread -fPIC -fwrapv -Wall -O2 \
-I "$CONDA_PREFIX/lib/python3.6/site-packages/numpy/core/include/" \
-I "$CONDA_PREFIX/include/python3.7m/" \
-o cema.so cema.c
```

Python code:
```python
{% include_relative src/e13_calc_ema_cython.py  %}
```

Report:
```txt
{% include_relative report/e13_calc_ema_cython.txt  %}
```

The result is **0.5s**. This is 4 times faster than numpy with slices.

Unfortunately, this code looks very tricky, and it is easy to make a mistake.
There is a simpler further.

**EMA with numba**

Numba allows you to compile you python code with JIT (runtime). 
But it adds some limitations on data types(numpy array and primitive types)
and operations which you can use, otherwise it won't compile.

Let's rewrite EMA function for numba.

Python code:
```python
{% include_relative src/e14_calc_ema_numba.py  %}
```

Report:
```txt
{% include_relative report/e14_calc_ema_numba.txt  %}
```

The performance is almost the same to cython, 
but JIT-compilationtakes **additional 0.27s**. 
But code looks more clear, you can remove `@jit`
and it will work with pure python as well. 
It simplifies the development a lot, so I prefer to use numba instead of cython.

## EMA - conclusions
- numpy with slices are considerably fast for most cases
- work directly with numpy and bypass xarray and pandas
- you can compile your code with cython or numba 
to work directly with underlying C-arrays in RAM
- cython is not python and it is more tricky than numba. 
But numba requires additional time(often small) for JIT compilation.

# [[Home]](/)


<script src='/assets/comments.js'></script>
