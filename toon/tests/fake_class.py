import numpy as np
from toon.input.base_input2 import BaseInput
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
        data = list()
        for i in self.data_dims:
            data.append(np.random.random(i))
        sleep(self.read_delay)
        if len(data) == 1:
            data = data[0]
        return self.time(), data
