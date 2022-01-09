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

## Generate the data 

Just run this script and it will generate 2000 series. Notice, that size of these series is about **0.5GB**. (You can generate more, but this amount is enough to demonstrate all the ideas.)
```bash
$ python generate_test_data.py
```
[source code](src/generate_test_data.py)

## Load data to RAM

First, we need to load the data. We'll try different approaches, and I'll show you how to reorganize your data and significantly reduce the time and RAM.

### Load with pure Python

 First, let's do it with pure Python.

```python
{% include_relative src/p1_e1_load.py  %}
```

# [[Home]](/)


<script src='/assets/comments.js'></script>
