import numpy as np
import matplotlib.pyplot as plt
from toon.tests.fake_class import FakeInput
from toon.input import MultiprocessInput
from psychopy.clock import monotonicClock

def read_fn(dev, length=5, period=1/60):
    out = []
    with dev as d:
        t0 = time()
        t1 = t0 + length
        while time() < t1:
            t3 = time()
            data = d.read()
            if data:
                print([d['time'] - t3 for d in data])
                out.extend(data)
                while time() < t3 + period:
                    pass
    return out

if __name__ == '__main__':
    time = monotonicClock.getTime
    single = FakeInput(data_dims=[[5]], read_delay=0.01, clock_source=time)

    dev = MultiprocessInput(single)
    out = read_fn(dev, length=240)

    times = [o['time'] for o in out]
    dtimes = np.diff(times)[1:]

    plt.plot(dtimes)
    plt.show()

    rr = plt.hist(dtimes, bins=100)
    plt.show(rr)

