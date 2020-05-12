from toon.anim.interpolators import LERP, SELECT
from toon.anim.interpolators import _test as _itest
from toon.anim.easing import (LINEAR, STEP,
                              SMOOTHSTEP, SMOOTHERSTEP,
                              QUADRATIC_IN, QUADRATIC_OUT, QUADRATIC_IN_OUT,
                              EXPONENTIAL_IN, EXPONENTIAL_OUT, EXPONENTIAL_IN_OUT,
                              ELASTIC_IN, ELASTIC_OUT, ELASTIC_IN_OUT,
                              BACK_IN, BACK_OUT, BACK_IN_OUT,
                              BOUNCE_IN, BOUNCE_OUT, BOUNCE_IN_OUT)
from toon.anim.easing import _test as _etest
from pytest import approx

interps = [LERP, SELECT]

easings = [LINEAR, STEP,
           SMOOTHSTEP, SMOOTHERSTEP,
           QUADRATIC_IN, QUADRATIC_OUT, QUADRATIC_IN_OUT,
           EXPONENTIAL_IN, EXPONENTIAL_OUT, EXPONENTIAL_IN_OUT,
           ELASTIC_IN, ELASTIC_OUT, ELASTIC_IN_OUT,
           BACK_IN, BACK_OUT, BACK_IN_OUT,
           BOUNCE_IN, BOUNCE_OUT, BOUNCE_IN_OUT]


def test_easings():
    for i in easings:
        assert(_etest(0.5, i) != 0)
        assert(_etest(0, i) == approx(0))
        assert(_etest(1, i) == approx(1))


def test_interps():
    for i in interps:
        assert(_itest(0, 1, 0, i) == 0)
        assert(_itest(0, 1, 1, i) == 1)
    assert(_itest(0, 1, 0.5, LERP) == 0.5)
