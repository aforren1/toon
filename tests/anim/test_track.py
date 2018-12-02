import pytest
from toon.anim.track import Track
from toon.anim.easing import *


def test_track():
    kfs = [(0, 0), (0.5, 1), (1.0, 2)]
    track = Track(kfs)
    assert(track.state == 'stopped')
    track.start(0)
    assert(track.update(0.3) == 0.6)
    assert(track.update(1.1) == 2)
    assert(track.state == 'stopped')
    track.start(2.0)
    assert(track.update(2.3) == pytest.approx(0.6, 0.0001))


def test_discrete():
    kfs = [(0, 'red'), (1, 'green'), (2, 'blue')]
    track = Track(kfs)
    assert(track.interpolator == select)
    track.start(0)
    assert(track.update(0.99) == 'red')
    assert(track.update(1.00) == 'green')


def test_other_easing():
    kfs = [(0, 0), (0.5, 1), (1.0, 2)]
    track = Track(kfs, easing=smootherstep)
    track.start(0)
    assert(track.update(1.0) == 2)


def test_other_interp():
    kfs = [(0, 0), (0.5, 1), (1.0, 2)]
    track = Track(kfs, interpolator=select)
    track.start(0)
    assert(track.update(0.499) == 0)
    assert(track.update(0.5) == 1)
