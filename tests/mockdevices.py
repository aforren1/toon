from toon.input.device import BaseDevice, Obs
from timeit import default_timer
import ctypes
import numpy as np


class Dummy(BaseDevice):
    counter = 0
    t0 = default_timer()

    class Num1(Obs):
        shape = (5,)
        ctype = ctypes.c_float

    class Num2(Obs):
        shape = (3, 3)
        ctype = ctypes.c_int

    @property
    def foo(self):
        return 3

    def read(self):
        dat = None
        self.counter += 1
        if self.counter % 10 == 0:
            dat = np.random.randint(5, size=(3, 3))
        while default_timer() - self.t0 < (1/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        return self.Returns(num1=self.Num1(t, np.random.random((5,))),
                            num2=self.Num2.new_obs(t, dat))


class DummyList(BaseDevice):
    counter = 0
    t0 = default_timer()

    class Num1(Obs):
        shape = (5,)
        ctype = ctypes.c_float

    class Num2(Obs):
        shape = (3, 3)
        ctype = ctypes.c_int

    def read(self):
        dat = None
        self.counter += 1
        if self.counter % 10 == 0:
            dat = np.random.randint(5, size=(3, 3))
        while default_timer() - self.t0 < (1/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        return [self.Returns(num1=self.Num1(t, np.random.random((5,))),
                             num2=self.Num2.new_obs(t, dat)),
                self.Returns(num1=self.Num1(t, np.random.random((5,))),
                             num2=self.Num2.new_obs(t, dat))]
