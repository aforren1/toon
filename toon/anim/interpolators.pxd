from cpython.ref cimport PyObject

cdef inline double lerp(const double v0, const double v1, const double t):
    return (1.0 - t) * v0 + t * v1

# need to be careful? https://github.com/cython/cython/issues/2589
cdef inline PyObject * select(PyObject * v0, PyObject * v1, const double t):
    return v0 if t < 1.0 else v1