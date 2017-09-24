"""
Temporary mouse class (for compat with our input devices)

Probably not ideal for experiments
"""
import numpy as np
from psychopy import core, event

class Mouse(object):
    def __init__(self, clock_source=core.monotonicClock,
                 multiprocess=False, win=None):
        self.time = clock_source
        self.multiprocess = multiprocess
        self._mouse = event.Mouse(visible=False, win=win)
        self._array = np.array([[3.0,2.1]])

    def __enter__(self):
        self._start_time = self.time.getTime()
        return self

    def read(self):
        self._array[0][0:2] = self._mouse.getPos()
        return self._array, self.time.getTime()

    def __exit__(self, type, value, traceback):
        pass
