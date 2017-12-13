from toon.input.mp_input import MultiprocessInput as MPI
from toon.input.mouse import Mouse
from toon.input.fake import FakeInput
from timeit import default_timer
import numpy as np
import ctypes

np.set_printoptions(precision=5, suppress=True)
#dev = MPI(Mouse)
dev = MPI(FakeInput, sampling_frequency=5000, data_shape=[[5, 2], [3]],
          data_type=[ctypes.c_double, ctypes.c_double])

with dev as d:
    t0 = default_timer()
    t1 = t0 + 120
    t2 = 0
    while default_timer() < t1:
        time, data = d.read()
        if time is not None:
            pass
            #print(np.diff(time))
            print(data)
        while default_timer() < t2:
            pass
        t2 = default_timer() + 1/60

