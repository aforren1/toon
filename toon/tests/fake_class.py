import numpy as np
from toon.input.base_input import BaseInput


class FakeInput(BaseInput):
    def __init__(self, read_delay=0, **kwargs):
        BaseInput.__init__(self, **kwargs)
        self.read_delay = read_delay

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def read(self):
        t0 = self.time()
        t1 = t0 + self.read_delay
        data = list()
        for i in self.data_dims:
            data.append(np.random.random(i))
        while self.time() < t1:
            pass
        if len(data) == 1:
            data = data[0]
        return self.time(), data
