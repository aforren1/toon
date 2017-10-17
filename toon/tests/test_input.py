import numpy as np
from toon.tests.fake_class import FakeInput
from toon.input import Input, BlamBirds, Hand, Keyboard
import os
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

single_data = Input(FakeInput, mp=False, data_dims=5, read_delay=0.001, clock_source=time)

multi_data = Input(FakeInput, mp=False, data_dims=[[5], [3, 2]],
                   clock_source=time, read_delay=0.001)

# if you want an idea of how fast the remote process spins,
# try setting the read_delay to 0 and looking at the period
# between readings
single_mp = Input(FakeInput, mp=True, data_dims=5, read_delay=0.001, clock_source=time)

multi_mp = Input(FakeInput, mp=True, data_dims=[[5], [3, 2]],
                 clock_source=time, read_delay=0.001)

def read_fn(dev):
    with dev as d:
        t0 = time()
        t1 = t0 + 3
        while t1 > time():
            t2 = time()
            t3 = 0.016 + t2
            timestamps, data = d.read()
            print('Frame start: ', str(t2 - t0))
            if timestamps is not None:
                print(timestamps - t0)
                print(data)
                data2 = data
            while t3 > time():
                pass
    assert_true(all([sh != 0 for sh in data2.shape]))


def test_reads():
    read_fn(single_data)
    read_fn(multi_data)
    read_fn(single_mp)
    read_fn(multi_mp)

@attr('birds')
def test_birds():
    birds = Input(BlamBirds, mp=True, ports=['COM5', 'COM6', 'COM7', 'COM8'])
    read_fn(birds)
    birds = Input(BlamBirds, mp=False, ports=['COM5', 'COM6', 'COM7', 'COM8'])
    read_fn(birds)

@attr('hand')
def test_hand():
    hand = Input(Hand, mp=True, nonblocking=True)
    read_fn(hand)
    hand = Input(Hand, mp=False, nonblocking=True)
    read_fn(hand)

@attr('force')
def test_force():
    ft = Input(ForceTransducers, mp=True)
    read_fn(ft)
    ft = Input(ForceTransducers, mp=False)
    read_fn(ft)

@attr('keyboard')
def test_keyboard():
    kb = Input(Keyboard, mp=True)
    read_fn(kb)
    kb = Input(Keyboard, mp=False)
    read_fn(kb)
