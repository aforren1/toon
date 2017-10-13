import numpy as np
from toon.tests.fake_class import FakeInput
from toon.input.base_input2 import MultiprocessInput
from time import sleep, time



single_data = FakeInput(data_dims = 5, read_delay=0.01)

multi_data = FakeInput(data_dims=[[5], [3, 2]])

single_mp = MultiprocessInput(device=FakeInput, nrow=20,
                              device_args={'data_dims': 5,
                                           'read_delay': 0.005})

multi_mp = MultiprocessInput(device=FakeInput, nrow=10,
                             device_args={'data_dims': [[5], [3,2]],
                                          'read_delay': 0.005})

def test_read(dev):
    with dev as d:
        t0 = time()
        t1 = t0 + 5
        while t1 > time():
            timestamps, data = d.read()
            if timestamps is not None:
                print(timestamps - t0)
                print(data)
            sleep(0.016)

test_read(single_data)

test_read(multi_data)

test_read(single_mp)

test_read(multi_mp)
