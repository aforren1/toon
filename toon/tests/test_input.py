import numpy as np
from toon.tests.fake_class import FakeInput
from toon.input import BlamBirds, Hand, Keyboard, MultiprocessPiper
import os
from unittest import TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_true
if os.sys.platform == 'win32':
    from toon.input import ForceTransducers

if 'TRAVIS' not in os.environ:
    from psychopy.clock import monotonicClock
    time = monotonicClock.getTime
else:
    from time import time

np.set_printoptions(precision=4)

def read_fn(dev):
    with dev as d:
        t0 = time()
        t1 = t0 + 3
        while t1 > time():
            t2 = time()
            t3 = 0.016 + t2
            data = d.read()
            #print('Frame start: ', str(t2 - t0))
            if data is not None:
                print(data)
            while t3 > time():
                pass

single_data = FakeInput(data_dims=5, read_delay=0.001, clock_source=time)

multi_data = FakeInput(data_dims=[[5], [3, 2]], clock_source=time, read_delay=0.001)

# if you want an idea of how fast the remote process spins,
# try setting the read_delay to 0 and looking at the period
# between readings
single_mp = MultiprocessPiper(single_data)

multi_mp = MultiprocessPiper(multi_data)

@attr(travis='yes')
def test_reads():
    read_fn(single_data)
    read_fn(multi_data)
    read_fn(single_mp)
    read_fn(multi_mp)

@attr(interactive=True)
class TestRealDevices(TestCase):

    def test_birds(self):
        birds = BlamBirds(ports=['COM5', 'COM6', 'COM7', 'COM8'])
        read_fn(birds)
        mp_birds = MultiprocessPiper(birds)
        read_fn(mp_birds)

    def test_hand(self):
        hand = Hand()
        read_fn(hand)
        mp_hand = MultiprocessPiper(hand)
        read_fn(mp_hand)

    def test_force(self):
        ft = ForceTransducers()
        read_fn(ft)
        mp_ft = MultiprocessPiper(ft)
        read_fn(mp_ft)

    def test_keyboard(self):
        """Note: In current montage, avoid importing keyboard on main process."""
        kb = Keyboard(keys = ['a', 's', 'd', 'f'])
        mp_kb = MultiprocessPiper(kb)
        read_fn(mp_kb)
