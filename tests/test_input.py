import os
from toon.input.mp_input import MultiprocessInput as MpI
from toon.input.mouse import Mouse
from toon.input.keyboard import Keyboard
from toon.input.hand import Hand
from toon.input.fake import FakeInput
from timeit import default_timer
import numpy as np
import ctypes
# import matplotlib.pyplot as plt

if os.name == 'nt':
    from toon.input.force_transducers import ForceTransducers


np.set_printoptions(precision=5, suppress=True)

if __name__ == '__main__':
    # dev = MpI(Mouse)
    # dev = MpI(Keyboard, keys=['a', 's', 'd', 'f'])
    # dev = MpI(Hand)
    # dev = MpI(ForceTransducers)
    dev = MpI(FakeInput, sampling_frequency=10000, data_shape=[[5]], data_type=[ctypes.c_double])

    read_times = []
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
                print(data)
                diffs.extend(np.diff(time))
            while default_timer() < t2:
                pass
            t2 = default_timer() + 0.01

# plt.plot(read_times)
# plt.show()
# plt.plot(diffs)
# plt.show()
