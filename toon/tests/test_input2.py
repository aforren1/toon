import numpy as np
from toon.tests.fake_class import FakeInput
from toon.input.base_input2 import Input
from psychopy.clock import monotonicClock

np.set_printoptions(precision=4)

mt = monotonicClock

single_data = Input(FakeInput,
                    mp=False,
                    data_dims=5,
                    read_delay=0.001,
                    clock_source=mt.getTime)

multi_data = Input(FakeInput,
                   mp=False,
                   data_dims=[[5], [3, 2]],
                   clock_source=mt.getTime,
                   read_delay=0.001)

single_mp = Input(FakeInput,
                  mp=True,
                  data_dims=5,
                  read_delay=0.001,
                  clock_source=mt.getTime)

multi_mp = Input(FakeInput,
                 mp=True,
                 data_dims=[[5], [3, 2]],
                 clock_source=mt.getTime,
                 read_delay=0.001)


def read_fn(dev):
    with dev as d:
        t0 = mt.getTime()
        t1 = t0 + 5
        while t1 > mt.getTime():
            t2 = mt.getTime()
            t3 = 0.016 + t2
            timestamps, data = d.read()
            if timestamps is not None:
                print(timestamps - t0)
                print(data)
            while t3 > mt.getTime():
                pass


def test_reads():
    read_fn(single_data)
    read_fn(multi_data)
    read_fn(single_mp)
    read_fn(multi_mp)
