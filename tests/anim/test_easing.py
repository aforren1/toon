from toon.anim.interpolators import lerp, select
from toon.anim.easing import (linear, step,
                              smoothstep, smootherstep,
                              quadratic_in, quadratic_out, quadratic_in_out,
                              exponential_in, exponential_out, exponential_in_out,
                              elastic_in, elastic_out, elastic_in_out,
                              back_in, back_out, back_in_out,
                              bounce_in, bounce_out, bounce_in_out)
from pytest import approx

interps = [lerp, select]

easings = [linear, step,
           smoothstep, smootherstep,
           quadratic_in, quadratic_out, quadratic_in_out,
           exponential_in, exponential_out, exponential_in_out,
           elastic_in, elastic_out, elastic_in_out,
           back_in, back_out, back_in_out,
           bounce_in, bounce_out, bounce_in_out]


def test_easings():
    for i in easings:
        assert(i(0.5) != 0)
        assert(i(0) == approx(0))
        assert(i(1) == approx(1))


def test_interps():
    for i in interps:
        assert(i(0, 1, 0) == 0)
        assert(i(0, 1, 1) == 1)
    assert(lerp(0, 1, 0.5) == 0.5)
