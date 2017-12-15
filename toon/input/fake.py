import numpy as np
from toon.input.base_input import BaseInput
from ctypes import c_double


class FakeInput(BaseInput):
    def __init__(self, **kwargs):
        super(FakeInput, self).__init__(**kwargs)
        self.data_shape = FakeInput.data_shapes(**kwargs)
        self.sampling_frequency = FakeInput.samp_freq(**kwargs)

    def __enter__(self):
        self.t1 = self.clock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self):
        time = self.clock()
        dat = [np.random.random(ds) for ds in self.data_shape]
        if len(self.data_shape) == 1:
            dat = dat[0]
        while self.clock() < self.t1:
            pass
        self.t1 = self.clock() + (1 / self.sampling_frequency)
        return time, dat

    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 100)

    @staticmethod
    def data_shapes(**kwargs):
        return kwargs.get('data_shape', [[5]])

    @staticmethod
    def data_types(**kwargs):
        return kwargs.get('data_type', [c_double])
