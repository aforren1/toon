from toon.input.device import BaseDevice
from timeit import default_timer
import ctypes
import numpy as np


class Dummy(BaseDevice):
    t0 = default_timer()
    ctype = ctypes.c_int
    shape = (5,)
    sampling_frequency = 500

    def read(self):
        data = np.random.randint(5, size=self.shape)
        while default_timer() - self.t0 < (1.0/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        return t, data


class NoData(Dummy):
    def read(self):
        return None


class Timebomb(Dummy):
    counter = 0

    def read(self):
        self.counter += 1
        if self.counter > 10:
            raise ValueError('Broke it.')
        return super().read()


class DummyList(Dummy):
    def read(self):
        out = []
        for i in range(5):
            out.append(super().read())
        return out


class SometimesNot(Dummy):
    counter = 0

    def read(self):
        self.counter += 1
        if self.counter % 2 == 0:
            return None
        return super().read()


class Point(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int), ('y', ctypes.c_int)]


class Rect(ctypes.Structure):
    _fields_ = [('ll', Point), ('ur', Point)]


class StructObs(BaseDevice):
    ctype = Rect
    sampling_frequency = 200
    shape = (2, 2)
    t0 = default_timer()

    def read(self):
        data = Rect()
        while default_timer() - self.t0 < (1.0/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        return t, data


class Incrementing(BaseDevice):
    ctype = int
    sampling_frequency = 100
    shape = (1,)
    t0 = default_timer()
    counter = 0

    def read(self):
        data = self.counter
        self.counter += 1
        while default_timer() - self.t0 < (1.0/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        return t, data
