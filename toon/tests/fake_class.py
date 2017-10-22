import numpy as np
from toon.input.base_input import BaseInput

class FakeInput(BaseInput):
    def __init__(self, read_delay=0, **kwargs):
        self.data_dims = kwargs.pop('data_dims', 3)
        BaseInput.__init__(self, **kwargs)
        self.read_delay = read_delay
        self.t1 = 0  # first period will be wrong

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def read(self):
        data = list()
        for i in self.data_dims:
            data.append(np.random.random(i))
        t0 = self.time()
        while self.time() < self.t1:
            pass
        if len(data) == 1:
            data = data[0]
        self.t1 = self.time() + self.read_delay
        return {'time': t0, 'data': data}
