import numpy as np
from toon.input.base_input2 import BaseInput, MultiprocessInput
from time import sleep, time

class FakeInput(BaseInput):
    def __init__(self,
                 clock_source=time,
                 data_dims=None,
                 read_delay=0):
        BaseInput.__init__(self, clock_source, data_dims)
        self.read_delay = read_delay
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        pass
    def read(self):
        if isinstance(self.data_dims, list):
            data = list()
            for i in self.data_dims:
                data.append(np.random.random(i))
        else:
            data = np.random.random(self.data_dims)
        sleep(self.read_delay)
        return self.time(), data

single_data = FakeInput(data_dims = 5)

multi_data = FakeInput(data_dims=[5, [3, 2]])

single_mp = MultiprocessInput(device=FakeInput, nrow=20,
                              device_args={'data_dims': 5})

multi_mp = MultiprocessInput(device=multi_data, nrow=10)

