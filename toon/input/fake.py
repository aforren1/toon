import numpy as np
from toon.input.mp_input import BaseInput
from ctypes import c_double

class FakeInput(BaseInput):
    def __init__(self, sampling_frequency=1000, **kwargs):
        super(FakeInput, self).__init__(sampling_frequency=sampling_frequency, **kwargs)
        self.data_shape = FakeInput.data_shapes(**kwargs)
        self.data_type = c_double
    def __enter__(self):
        self.t1 = self.clock()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def read(self):
        time = self.clock()
        dat = [np.random.random(ds) for ds in self.data_shape]
        while self.clock() < self.t1:
            pass
        self.t1 = self.clock() + (1/self.sampling_frequency)
        return time, dat
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 100)
    def data_shapes(**kwargs):
        return kwargs.get('data_shape', [[5]])
    def data_types(**kwargs):
        pass