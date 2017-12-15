from toon.input import BaseInput
import ctypes


class HetInput(BaseInput):
    def __init__(self, sampling_frequency=100, **kwargs):
        super(HetInput, self).__init__(sampling_frequency=sampling_frequency, **kwargs)

    def __enter__(self):
        self.t1 = self.clock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self):
        time = self.clock()
        data = ['r', 32]
        while self.clock() < self.t1:
            pass
        self.t1 = self.clock() + (1 / self.sampling_frequency)
        return time, data

    @staticmethod
    def samp_freq(**kwargs):
        return 100

    @staticmethod
    def data_types(**kwargs):
        return [ctypes.c_char, ctypes.c_uint16]

    @staticmethod
    def data_shapes(**kwargs):
        return [[1], [1]]
