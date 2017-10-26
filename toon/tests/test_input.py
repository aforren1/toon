import os
import itertools
from unittest import TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_less
import numpy as np
from numpy.testing import assert_allclose
from toon.tests.fake_class import FakeInput
from toon.input import BlamBirds, Hand, Keyboard, MultiprocessInput

if os.sys.platform == 'win32':
    from toon.input import ForceTransducers

if 'TRAVIS' not in os.environ:
    from psychopy.clock import monotonicClock
    time = monotonicClock.getTime
else:
    from timeit import default_timer
    time = default_timer

def read_fn(dev):
    out = []
    with dev as d:
        t0 = time()
        t1 = t0 + 3
        while t1 > time():
            t2 = time()
            t3 = 0.016 + t2
            data = d.read()
            if data is not None:
                if isinstance(data, list):
                    out.extend(data)
                else:
                    out.append(data)
            while t3 > time():
                pass
    return out


@attr(travis='yes')
def test_reads():
    delays = [0.01, 0.001, 0.0005]
    data_dims = [[[5]], [[2,3], [4,5]]]
    priority = ['norm', 'high']
    garbage = [True, False]
    for i in list(itertools.product(data_dims, delays, priority, garbage)):
        print('Testing: ' + str(i))
        dev = FakeInput(data_dims=i[0], read_delay=i[1])
        mpdev = MultiprocessInput(dev, priority=i[2], disable_gc=i[3])
        out = read_fn(dev)
        delta = np.diff([o['time'] for o in out])[1:]
        print(np.median(delta))
        print(np.var(delta))
        assert_allclose(np.median(delta), 0.016, atol=1e-4)
        assert_less(np.var(delta), 1e-6)
        # out = read_fn(mpdev)
        # print(out)
        # delta = np.diff([o['time'] for o in out])[1:]
        # print(np.median(delta))
        # print(np.var(delta))
        # assert_allclose(np.median(delta), i[1], atol=1e-4)
        # assert_less(np.var(delta), 1e-6)


@attr(interactive=True)
class TestRealDevices(TestCase):

    def test_birds(self):
        birds = BlamBirds(ports=['COM5', 'COM6', 'COM7', 'COM8'])
        read_fn(birds)
        mp_birds = MultiprocessInput(birds)
        read_fn(mp_birds)

    def test_hand(self):
        hand = Hand()
        read_fn(hand)
        mp_hand = MultiprocessInput(hand)
        read_fn(mp_hand)

    def test_force(self):
        ft = ForceTransducers()
        read_fn(ft)
        mp_ft = MultiprocessInput(ft)
        read_fn(mp_ft)

    def test_keyboard(self):
        """Note: In current montage, avoid importing keyboard on main process."""
        kb = Keyboard(keys = ['a', 's', 'd', 'f'])
        mp_kb = MultiprocessInput(kb)
        read_fn(mp_kb)
