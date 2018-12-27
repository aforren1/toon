import os

from timeit import default_timer


class MonoClock(object):
    """A stripped-down version of psychopy's clock.MonotonicClock.

    I wanted to avoid importing pyglet on the remote process, in case that causes any headache.
    """

    def __init__(self):
        # this is sub-millisec timer in python
        self.default_timer = default_timer
        self._start_time = default_timer()

    def get_time(self):
        """Returns the current time on this clock in secs (sub-ms precision)
        """
        return self.default_timer() - self._start_time

    def getTime(self):
        """Alias get_time so we can set the default psychopy clock
        """
        return self.get_time()

    @property
    def start_time(self):
        return self._start_time


mono_clock = MonoClock()
