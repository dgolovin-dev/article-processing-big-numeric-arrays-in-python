# Processing big numeric arrays in python

## Intro

Hello. 

As you know, Python is an interpreted language and it is not very fast at processing data. C, Java or any other compilable language is much faster. However, Python is very popular among data scientists and they use it for processing data. But if you want to reach acceptable performance you **MUST** use some *special libraries* which allow you to use the performance benefits of compiled languages.

In this article I will talk about *numpy*, *pandas*, *xarray*, *cython*, *numba*. And I will show you a real example of how to use them properly and boost the performance hundreds of times. The source code of the example is available on github, so you can download and check them by yourself.


## Task

**Definition**: *Calculate [Exponential Moving Averages](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average) for all columns of 2000 stocks daily data series.*

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

### Load with pure Python

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

### Load with Pandas

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


## Load with pandas (7 columns)
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

It looks acceptable, but we can do it better.

# [[Home]](/)


<script src='/assets/comments.js'></script>
