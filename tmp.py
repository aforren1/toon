import matplotlib.pyplot as plt
from toon.input import MpDevice
from tests.input.mockdevices import Incrementing
import numpy as np
from time import sleep

Incrementing.sampling_frequency = 1000
dev = MpDevice(Incrementing())
with dev:
    times, dats = [], []
    for i in range(60*240):
        data = dev.read()
        if data:
            times.append(data[0])
            dats.append(data[1])
            sleep(0.016)
times = np.hstack(times)
vals = np.hstack(dats)

plt.plot(np.diff(times))
plt.show()
