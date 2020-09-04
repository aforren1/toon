from libc.stdint cimport uint64_t
cimport cython

cdef extern from "clock.h":
    ctypedef struct _time_state_t:
        pass
    void init_clock(_time_state_t *reference)
    uint64_t clock_now(_time_state_t *reference)
    void set_ref(_time_state_t *reference, uint64_t value)
    uint64_t get_ref(_time_state_t *reference)
    
@cython.final
cdef class MonoClock:
    cdef _time_state_t reference
    def __cinit__(self, const bint relative=True, ns=None):
        init_clock(&self.reference)
        if not relative:
            set_ref(&self.reference, 0)
        if ns is not None:
            set_ref(&self.reference, ns)

    cpdef uint64_t get_time_ns(self):
        return clock_now(&self.reference)
    
    cpdef double get_time(self):
        return <double>self.get_time_ns() * 1e-9
    
    cpdef double getTime(self):
        return self.get_time()
    
    cpdef uint64_t dump_origin_ns(self):
        return get_ref(&self.reference)
    
    def __reduce__(self):
        return (MonoClock, (True, self.dump_origin_ns()))

mono_clock = MonoClock.__new__(MonoClock)
