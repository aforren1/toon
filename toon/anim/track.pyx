#cython: boundscheck=False
#cython: nonecheck=False
#cython: wraparound=False
#cython: infertypes=True
#cython: initializedcheck=False
#cython: cdivision=True
from cpython.ref cimport PyObject

import numpy as np
cimport numpy as np
from .interpolators import LERP, SELECT
from .interpolators cimport lerp, select
from .easing import LINEAR
from .easing cimport EaseFn, eases


cdef class Track:
    
    cdef EaseFn easing
    cdef int interpolator
    cdef np.float64_t[::1] times
    cdef list vals
    cdef int prev_index
    cdef int len_times

    def __init__(self, data, interpolator=LERP, easing=LINEAR):
        self.interpolator = interpolator
        self.easing = eases[<int>easing]

        self.times = np.array([d[0] for d in data], dtype=np.float64)
        self.len_times = self.times.shape[0]
        self.vals = [d[1] for d in data] # we don't really know the datatype here
        self.prev_index = 0

        if not isinstance(self.vals[0], (float, int)):
            self.interpolator = SELECT
            self.easing = eases[<int>LINEAR]

    cpdef at(self, const double time):
        if time <= self.times[0]:
            self.prev_index = 0
            return self.vals[0]
        if time >= self.times[self.len_times - 1]:
            self.prev_index = self.len_times - 1
            return self.vals[self.len_times - 1]
        if time == self.times[self.prev_index]:
            return self.vals[self.prev_index]
        cdef double time_scaled, time_warp
        cdef int reference, target
        time_scaled, reference, target = get_warptime(self.prev_index, time, 
                                                    self.len_times, &self.times[0])
        self.prev_index = reference
        time_warp = self.easing(time_scaled)
        if self.interpolator == 0: # LERP
            return lerp(self.vals[reference], self.vals[target], time_warp)
        return <object>select(<PyObject *>self.vals[reference], <PyObject *>self.vals[target], time_warp)

    cpdef duration(self):
        return self.times[self.len_times - 1]

cdef (double, int, int) get_warptime(const int prev_index, const double time, 
                            const int len_times, const double* times) nogil:
    cdef int index
    cdef int reference
    cdef int target
    cdef double sign = time - times[prev_index]
    cdef double goal_time, new_time

    if sign > 0:
        for index in range(prev_index + 1, len_times):
            if time < times[index]:
                break
        
        reference = index - 1
        target = index
    else:
        for index in range(prev_index - 1, -1, -1):
            if time > times[index]:
                break
        
        reference = index
        target = index + 1
    
    goal_time = times[target] - times[reference]
    new_time = time - times[reference]
    return 1.0 - ((goal_time - new_time)/goal_time), reference, target
