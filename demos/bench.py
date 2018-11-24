from toon.input.device import BaseDevice, Obs
from ctypes import c_double
from timeit import default_timer
from functools import reduce
from operator import mul
# 3 dims: sampling frequency, volume (e.g. high-dim # obs), num of unique Obs


class Dummy(BaseDevice):
    counter = 0
    t0 = default_timer()

    class Num(Obs):
        shape = (256,)
        ctype = c_double

    def read(self):
        while default_timer() - self.t0 < (1/self.sampling_frequency):
            pass
        self.t0 = default_timer()
        t = self.clock()
        self.counter += 1
        return self.Returns(self.Num(t,
                                     [self.counter] * reduce(mul, self.Num.shape, 1)))


if __name__ == '__main__':
    from time import sleep
    import matplotlib.pyplot as plt
    from statistics import median
    from toon.input.mpdevice import MpDevice

    Dummy.sampling_frequency = 1000
    dev = MpDevice(Dummy)

    vals = []

    with dev:
        t0 = default_timer()
        while default_timer() - t0 < 20:
            t1 = default_timer()
            dat = dev.read()
            if dat.any():
                vals.append(default_timer() - t1)
                sleep(0.016)
    vals = vals[10:]  # first couple are pathological
    print('Worst case: %f' % max(vals))
    print('Median: %f' % median(vals))
    plt.plot(vals)
    plt.show()
