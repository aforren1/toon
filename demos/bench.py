from timeit import default_timer
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
from toon.input import BaseDevice, MpDevice, make_obs


class TestDevice(BaseDevice):
    def __init__(self, obses, device_sampling_freq):
        for count, val in enumerate(obses):
            setattr(self, 'Obs%s' % count, val)
        self.obses = obses
        self.device_sampling_freq = device_sampling_freq
        self.t0 = default_timer()
        super(TestDevice, self).__init__()

    def read(self):
        data = []
        while default_timer() - self.t0 < (1.0/self.device_sampling_freq):
            pass
        self.t0 = default_timer()
        for i in self.obses:
            data.append(i(self.clock(), np.random.random(i.shape)))
        return data


if __name__ == '__main__':
    # user-side sampling period: 1/144, 1/60, 1/10, 1
    # device sampling freq: 10, 100, 1000, 5000
    # number of Obs: 1, 2, 5, 10
    # dims of Obs: (1,), (10,), (100,), (10, 10)
    # buffer size: 1, 10, 100, 1000
    user_sampling_period = 1.0/60
    device_sampling_freq = 1000
    number_of_obs = 1
    obs_dims = (1000,)
    buffer_size = 100
    n_samples = 1000

    obses = []
    for i in range(number_of_obs):
        obses.append(make_obs('Obs%s' % i, obs_dims, float))

    times = []
    dev = MpDevice(TestDevice(obses, device_sampling_freq), buffer_len=buffer_size)
    with dev:
        for i in range(n_samples):
            t0 = default_timer()
            res = dev.read()
            t1 = default_timer() - t0
            times.append(t1)
            sleep(user_sampling_period)
    print('Worst: %f' % np.max(times))
    print('Median: %f' % np.median(times))
    plt.plot(times)
    plt.show()
