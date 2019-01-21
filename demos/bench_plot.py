from toon.input import mono_clock
from timeit import default_timer
from time import sleep
import numpy as np
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
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # fixed
    user_sampling_period = 1.0/60
    device_sampling_freq = [1, 10, 100, 1000, 5000]
    # parameter space to explore
    number_of_obs = [1, 2, 5, 10]
    obs_dims = [(1,), (10,), (100,), (1000,)]
    n_samples = 1000

    median_res = []

    for i in number_of_obs:
        for j in obs_dims:
            for k in device_sampling_freq:
                obses = []
                for n in range(i):
                    obses.append(make_obs('Obs%s' % n, j, float))
                times = []
                dev = MpDevice(TestDevice(obses, k), buffer_len=k)
                with dev:
                    for o in range(n_samples):
                        t0 = mono_clock.get_time()
                        res = dev.read()
                        t1 = mono_clock.get_time()
                        times.append(t1 - t0)
                        sleep(user_sampling_period)
                times = times[5:]
                print("""# Obs: %i, Elements per Obs: %i, Device sampling frequency: %i,
                        Worst: %f, Median: %f""" %
                      (i, j[0], k, np.max(times), np.median(times)))
                median_res.append({'number_of_obs': i,
                                   'obs_dims': j[0],
                                   'device_freq': k,
                                   'median_time': np.median(times)})

    x = np.array([x['obs_dims'] for x in median_res])
    y = np.array([x['number_of_obs'] for x in median_res])
    z = np.array([x['device_freq'] for x in median_res])
    colors = np.array([x['median_time'] for x in median_res])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    cmhot = plt.get_cmap('hot')
    rr = ax.scatter(np.log(x), np.log(y), np.log(z),
                    c=np.log(colors), cmap=cmhot, s=100)
    cbar = fig.colorbar(rr, ax=ax)
    ax.set_xlabel('Observation dimensions (log)')
    ax.set_ylabel('Number of observations (log)')
    ax.set_zlabel('Device sampling frequency (log)')

    # click on the colorbar to get the exponentiated val (i.e. original scale)
    def on_pick(event):
        val = event.mouseevent.ydata
        print('Time: %f' % np.exp(val))

    cbar.ax.set_picker(5)
    fig.canvas.mpl_connect('pick_event', on_pick)

    plt.show()
