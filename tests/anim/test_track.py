import pytest
from toon.anim.track import Track
from toon.anim.easing import *
from toon.anim.interpolators import lerp, select


def test_track():
    kfs = [(0, 0), (0.5, 1), (1.0, 2)]
    track = Track(kfs)
    assert(track.at(0.3) == 0.6)
    assert(track.at(1.1) == 2)
    assert(track.at(2.3) == 2)


def test_discrete():
    kfs = [(0, 'red'), (1, 'green'), (2, 'blue')]
    track = Track(kfs)
    assert(track.interpolator == select)
    assert(track.at(0.99) == 'red')
    assert(track.at(1.00) == 'green')


def test_other_easing():
    kfs = [(0, 0), (0.5, 1), (1.0, 2)]
    track = Track(kfs, easing=smootherstep)
    assert(track.at(1.0) == 2)


def test_other_interp():
    kfs = [(0, 0), (0.5, 1), (1.0, 2)]
    track = Track(kfs, interpolator=select)
    assert(track.at(0.499) == 0)
    assert(track.at(0.5) == 1)
