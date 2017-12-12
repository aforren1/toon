import abc
import multiprocessing as mp
import ctypes
from numbers import Number
from timeit import default_timer
import numpy as np

class BaseInput(abc.ABC):
    @abc.abstractmethod
    def __init__(self, clock=default_timer, sampling_frequency=None, **kwargs):
        self.clock = clock
        self.sampling_frequency = sampling_frequency
    @abc.abstractmethod
    def __enter__(self):
        pass
    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    @abc.abstractmethod
    def read(self):
        pass
    @staticmethod
    @abc.abstractmethod
    def samp_freq(**kwargs):
        # if it's directly a kwarg, can just do
        # kwargs.get('sampling_frequency', 100)?
        # I don't think setting directly would be the best
        # (we use this to calculate how big the shared array should be)
        pass
    @staticmethod
    @abc.abstractmethod
    def data_shapes(**kwargs):
        # must be list of lists, e.g.
        # [[2,3], [8]]
        pass
    @staticmethod
    @abc.abstractmethod
    def data_types(**kwargs):
        # list, e.g.
        # [ctypes.c_int32, ctypes.c_double]
        # [ctypes.c_char]
        # if single element, will be coerced to list
        pass
