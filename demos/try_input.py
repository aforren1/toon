import os
from toon.input import MultiprocessInput as MpI
from toon.input.mouse import Mouse
from toon.input.keyboard import Keyboard
from toon.input.hand import Hand
from toon.input.fake import FakeInput
from toon.input.clock import mono_clock
import numpy as np
import ctypes
# import matplotlib.pyplot as plt

if os.name == 'nt':
    from toon.input.force_keyboard import ForceKeyboard


np.set_printoptions(precision=5, suppress=True)

if __name__ == '__main__':
    default_timer = mono_clock.get_time
    dev = MpI(Mouse, clock=default_timer)
    # dev = MpI(Keyboard, keys=['a', 's', 'd', 'f'])
    # dev = MpI(Hand)
    # dev = MpI(ForceKeyboard)
    # dev = MpI(FakeInput, sampling_frequency=1000, data_shape=[[5]], data_type=[ctypes.c_double])
    read_times = []
    diffs = []
    dev.start()
    t0 = default_timer()
    t1 = t0 + 10
    t2 = 0
    while default_timer() < t1:
        t0 = default_timer()
        time, data = dev.read()
        t3 = default_timer()
        read_times.append(t3 - t0)
        if time is not None:
            print('Frame time: ' + str(t0))
            print(time)
            diffs.extend(np.diff(time))
        while default_timer() < t2:
            pass
        t2 = default_timer() + 0.01
    dev.stop()

# plt.plot(read_times)
# plt.show()
# plt.plot(diffs)
# plt.show()