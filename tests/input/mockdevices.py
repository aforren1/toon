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
            dat = np.random.randint(5, size=self.Num2.shape)
        while default_timer() - self.t0 < (1/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        return self.Returns(num1=self.Num1(t, np.random.random(self.Num1.shape)),
                            num2=self.Num2(t, dat))


class SingleResp(BaseDevice):
    t0 = default_timer()
    sampling_frequency = 1000

    class Num1(Obs):
        shape = (100,)
        ctype = float

    def read(self):
        while default_timer() - self.t0 < (1/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        return self.Returns(self.Num1(t, np.random.random(self.Num1.shape)))


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
            dat = np.random.randint(5, size=self.Num2.shape)
        while default_timer() - self.t0 < (1/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        return [self.Returns(num1=self.Num1(t, np.random.random(self.Num1.shape)),
                             num2=self.Num2(t, dat)),
                self.Returns(num1=self.Num1(t, np.random.random(self.Num1.shape)),
                             num2=self.Num2(t, dat))]


if __name__ == '__main__':  # pragma: no cover
    from time import time, sleep
    from timeit import default_timer
    import matplotlib.pyplot as plt
    from toon.input.mpdevice import MpDevice
    Dummy.sampling_frequency = 1000
    dev = MpDevice(DummyList)
    times = []
    with dev:
        start = time()
        while time() - start < 10:
            t0 = default_timer()
            dat = dev.read()
            t1 = default_timer()
            if dat[0].data is not None:
                dff = t1 - t0
                # print(dff)
                # print(dat.num1.data.shape)
                # print(np.diff(dat.num1.time))
                print(dat.num2.time)
                times.append(np.diff(dat[0].time[::2]))
                sleep(0.016)
    plt.plot(np.hstack(times))
    plt.show()
