#cython: boundscheck=False
#cython: nonecheck=False
#cython: wraparound=False
#cython: infertypes=True
#cython: initializedcheck=False
#cython: cdivision=True
from libc.math cimport sin, pi, pow

cpdef enum easings:
    LINEAR
    STEP
    SMOOTHSTEP
    SMOOTHERSTEP
    QUADRATIC_IN
    QUADRATIC_OUT
    QUADRATIC_IN_OUT
    EXPONENTIAL_IN
    EXPONENTIAL_OUT
    EXPONENTIAL_IN_OUT
    ELASTIC_IN
    ELASTIC_OUT
    ELASTIC_IN_OUT
    BACK_IN
    BACK_OUT
    BACK_IN_OUT
    BOUNCE_IN
    BOUNCE_OUT
    BOUNCE_IN_OUT

cdef inline double pihalf = pi / 2

cdef inline double linear(const double x):
    return x


cdef inline double step(const double x):
    return 0.0 if x < 0.5 else 1.0


cdef inline double smoothstep(const double x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    return (3.0 - 2.0 * x) * pow(x, 2)

cdef inline double smootherstep(const double x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    return pow(x, 3) * (x * (x * 6.0 - 15.0) + 10.0)

cdef inline double quadratic_in(const double x):
    return pow(x, 2)


cdef inline double quadratic_out(const double x):
    return -x * (x - 2.0)


cdef inline double quadratic_in_out(const double x):
    if x < 0.5:
        return 2.0*pow(x, 2)
    return 1.0 - 2.0*pow(1.0 - x, 2)


cdef inline double exponential_in(const double x):
    return 0.0 if x <= 0.0 else pow(2.0, 10.0 * (x - 1.0))


cdef inline double exponential_out(const double x):
    return 1.0 if x >= 1.0 else 1.0 - pow(2.0, -10.0 * x)


cdef inline double exponential_in_out(const double x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    if x < 0.5:
        return 0.5 * pow(2.0, 20.0*x - 10.0)
    return 1.0 - 0.5 * pow(2.0, 10.0 - 20.0 * x)


cdef inline double elastic_in(const double x):
    return pow(2.0, 10.0 * (x - 1.0)) * sin(13.0 * pihalf * x)


cdef inline double elastic_out(const double x):
    return 1.0 - pow(2.0, -10.0 * x) * sin(13.0 * pihalf * (x + 1.0))


cdef inline double elastic_in_out(const double x):
    if x < 0.5:
        return 0.5 * pow(2.0, 10.0 * (2.0 * x - 1.0)) * sin(13.0 * pi * x)
    return 1.0 - 0.5 * pow(2.0, 10.0 * (1.0 - 2.0 * x)) * sin(13.0 * pi * x)


cdef inline double back_in(const double x):
    return x * (x * x - sin(pi * x))


cdef inline double back_out(const double x):
    inv = 1.0 - x
    return 1 - inv*(inv*inv - sin(pi*inv))


cdef inline double back_in_out(const double x):
    if x < 0.5:
        x2 = 2.0 * x
        return 0.5 * x2 * (x2 * x2 - sin(pi * x2))
    inv = 2.0 - 2.0 * x
    return 1.0 - 0.5 * inv * (inv * inv - sin(pi * inv))

cdef inline double bounce_out(const double x):
    if x == 0:
        return 0
    if x < 4.0/11.0:
        return 121.0*x*x/16.0
    if x < 8.0/11.0:
        return 363.0/40.0*x*x - 99.0/10.0 * x + 17.0/5.0
    if x < 9.0/10.0:
        return 4356.0/361.0*x*x - 35442.0/1805.0*x + 16061.0/1805.0
    if x == 1:
        return 1
    return 54.0/5.0 * x*x - 513.0/25.0*x + 268.0/25.0


cdef inline double bounce_in(const double x):
    return 1.0 - bounce_out(1.0 - x)


cdef inline double bounce_in_out(const double x):
    if x < 0.5:
        return 0.5 * bounce_in(2*x)
    return 0.5 * bounce_out(2.0 * x - 1) + 0.5

cpdef double _test(double x, easings ease):
    return eases[<int>ease](x)

eases[:] = [linear, step, smoothstep, smootherstep, quadratic_in,
            quadratic_out, quadratic_in_out, exponential_in, exponential_out,
            exponential_in_out, elastic_in, elastic_out, elastic_in_out,
            back_in, back_out, back_in_out, bounce_in, bounce_out, bounce_in_out]
