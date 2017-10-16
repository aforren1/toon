import numpy as np
from toon.tests.fake_class import FakeInput
from toon.input.base_input2 import Input
import os
if 'TRAVIS' not in os.environ:
    from psychopy.clock import monotonicClock
    time = monotonicClock.getTime
else:
    from time import time

np.set_printoptions(precision=4)

single_data = Input(FakeInput,
                    mp=False,
                    data_dims=5,
                    read_delay=0.001,
                    clock_source=time)

multi_data = Input(FakeInput,
                   mp=False,
                   data_dims=[[5], [3, 2]],
                   clock_source=time,
                   read_delay=0.001)

single_mp = Input(FakeInput,
                  mp=True,
                  data_dims=5,
                  read_delay=0.001,
                  clock_source=time)

multi_mp = Input(FakeInput,
                 mp=True,
                 data_dims=[[5], [3, 2]],
                 clock_source=time,
                 read_delay=0.001)


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
            while t3 > time():
                pass


def test_reads():
    read_fn(single_data)
    read_fn(multi_data)
    read_fn(single_mp)
    read_fn(multi_mp)
