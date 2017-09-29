"""
Temporary mouse class (for compat with our input devices)

Probably not ideal for experiments
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import numpy as np
from psychopy import event
from toon.input.base_input import DummyTime

class Mouse(object):
    def __init__(self, clock_source=DummyTime,
                 multiprocess=False, win=None):
        self.time = clock_source
        self.multiprocess = multiprocess
        self.win = win
        self._mouse = event.Mouse(win=win)
        self._array = np.array([[3.0,2.1]])
        self.name = type(self).__name__

    def __enter__(self):
        self._start_time = self.time.getTime()
        return self

    def read(self):
        pos = self._mouse.getPos()
        self._array[0][0:2] = pos
        return self._array, self.time.getTime()

    def __exit__(self, type, value, traceback):
        pass
