#cython: boundscheck=False
#cython: nonecheck=False
#cython: wraparound=False
#cython: infertypes=True
#cython: initializedcheck=False
#cython: cdivision=True

cpdef enum interpolations:
    LERP
    SELECT

cpdef _test(a, b, const double t, interpolations inter):
    if inter == LERP:
        return lerp(a, b, t)
    return <object>select(<PyObject *>a, <PyObject *>b, t)
