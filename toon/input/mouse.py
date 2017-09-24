"""
Temporary mouse class (for compat with our input devices)

Probably not ideal for experiments
"""

from psychopy import core, event

class Mouse(object):
    def __init__(self, clock_source=core.monotonicClock,
                 multiprocess=False, win=None):
        self.time = clock_source
        self.multiprocess = multiprocess
        self._mouse = event.Mouse(visible=False, win=win)

    def __enter__(self):
        self._start_time = self.time.getTime()

    def read(self):
        return self._mouse.getPos(), self.time.getTime()

    def __exit__(self, type, value, traceback):
        pass
