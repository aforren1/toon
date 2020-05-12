from libcpp cimport bool

cdef extern from "clock.hpp" namespace "toon":
    cdef cppclass CMonoClock "toon::MonoClock":
        CMonoClock() except +
        CMonoClock(const bool relative, const long long ns) except +
        long long get_time_ns()
        double get_time()
        long long dump_origin_ns()

cdef class MonoClock:
    cdef CMonoClock cclk
    def __cinit__(self, const bool relative=True, ns=-1):
        self.cclk = CMonoClock(relative, ns)
    def get_time_ns(self) -> int:
        return self.cclk.get_time_ns()
    def get_time(self) -> float:
        return self.cclk.get_time()
    def getTime(self) -> float:
        return self.cclk.get_time()
    def dump_origin_ns(self) -> int:
        return self.cclk.dump_origin_ns()
    def __reduce__(self):
        return (MonoClock, (True, self.dump_origin_ns()))


mono_clock = MonoClock.__new__(MonoClock)
