from libc.math cimport NAN, isnan
import numpy as np
cimport numpy as np
cimport cython

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
def c_ema(np.ndarray[DTYPE_t, ndim = 2] data, DTYPE_t n):
    cdef DTYPE_t k = 2.0 / (1.0 + n)
    cdef DTYPE_t _k = 1 - k
    cdef int xmax = data.shape[0]
    cdef int ymax = data.shape[1]
    cdef np.ndarray res = np.zeros([xmax, ymax], dtype=DTYPE)
    cdef double[:,:] resd = res
    cdef DTYPE_t prev_ema = NAN
    cdef DTYPE_t cur_ema = NAN
    for x in range(0, xmax, 1):
        prev_ema = NAN
        for y in range(0, ymax, 1):
            cur_ema = data[x, y]
            if not isnan(prev_ema):
                if isnan(cur_ema):
                    cur_ema = prev_ema
                else:
                    cur_ema = cur_ema * k + prev_ema * _k
            resd[x, y] = cur_ema
            prev_ema = cur_ema
    return res

