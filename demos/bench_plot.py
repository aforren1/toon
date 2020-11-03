from toon.util import mono_clock
from timeit import default_timer
from time import sleep
import numpy as np
from toon.input import BaseDevice, MpDevice


class TestDevice(BaseDevice):
    ctype = float

    def __init__(self, device_sampling_freq, shape=(1,)):
        self.device_sampling_freq = device_sampling_freq
        self.t0 = default_timer()
        self.shape = shape
        super().__init__()

    def read(self):
        time = self.clock()
        data = np.random.random(self.shape)
        while default_timer() - self.t0 < (1.0/self.device_sampling_freq):
            pass
        self.t0 = default_timer()
        return time, data


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # fixed
    user_sampling_period = 1.0/60
    n_samples = 500
    # parameter space to explore
    device_sampling_freq = [10, 100, 1000, 5000]
    obs_dims = [(1,), (10,), (100,), (1000,)]

    median_res = []

    for j in obs_dims:
        for k in device_sampling_freq:
            times = []
            dev = MpDevice(TestDevice(device_sampling_freq=k, shape=j),
                           buffer_len=1000)
            with dev:
                for o in range(n_samples):
                    t0 = mono_clock.get_time()
                    res = dev.read()
                    t1 = mono_clock.get_time()
                    times.append(t1 - t0)
                    sleep(user_sampling_period)
            times = times[5:]
            print("""# shape: %s, sampling frequency: %i, Worst: %f, Median: %f""" %
                  (j, k, np.max(times), np.median(times)))
            plt.plot(times)
            plt.show()
            median_res.append({'dims': np.product(j),
                               'device_freq': k,
                               'median_time': np.median(times)})

    x = np.array([x['dims'] for x in median_res])
    y = np.array([x['device_freq'] for x in median_res])
    z = np.array([x['median_time'] for x in median_res])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    rr = ax.scatter(np.log(x), np.log(y), np.log(z),
                    s=100)
    ax.set_xlabel('Observation dimensions (log)')
    ax.set_ylabel('Device frequency (log)')
    ax.set_zlabel('Median time (log)')

    plt.show()
