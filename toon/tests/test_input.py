from toon.input.mp_input import MultiprocessInput as MPI
from toon.input.mouse import Mouse
from toon.input.fake import FakeInput
from timeit import default_timer
import numpy as np
import ctypes
import matplotlib.pyplot as plt

np.set_printoptions(precision=5, suppress=True)
#dev = MPI(Mouse)
dev = MPI(FakeInput, sampling_frequency=10000, data_shape=[[20]],
          data_type=[ctypes.c_double, ctypes.c_double])

read_times = []
num_samples = []
last_sample_and_ret = []
diffs = []
with dev as d:
    t0 = default_timer()
    t1 = t0 + 30
    t2 = 0
    while default_timer() < t1:
        t0 = default_timer()
        time, data = d.read()
        t3 = default_timer()
        read_times.append(t3 - t0)
        if time is not None:
            num_samples.append(len(time))
            last_sample_and_ret.append(t3 - time[-1])
            diffs.extend(np.diff(time))
        while default_timer() < t2:
            pass
        t2 = default_timer() + 0.01

plt.plot(read_times)
plt.show()
plt.plot(num_samples)
plt.show()
plt.plot(last_sample_and_ret)
plt.show()