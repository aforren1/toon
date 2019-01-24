import os
import time

# From Stack Overflow
# User linusg https://stackoverflow.com/users/5952681/linusg
# https://stackoverflow.com/a/38463185/2690232
if os.name == 'nt':
    import ctypes
    import ctypes.wintypes as cwt

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    current_counter = cwt.LARGE_INTEGER()
    frequency = cwt.LARGE_INTEGER()
    kernel32.QueryPerformanceFrequency(ctypes.byref(frequency))
    frequency = float(frequency.value)  # force non-integer division

    def get_time():
        kernel32.QueryPerformanceCounter(ctypes.byref(current_counter))
        return current_counter.value / frequency

else:
    from time import monotonic as get_time


class MonoClock(object):
    """A stripped-down version of psychopy's clock.MonotonicClock.
    I wanted to avoid importing pyglet on the remote process, in case that causes any headache.
    """

    def __init__(self):
        # this is sub-millisec timer in python
        self._start_time = get_time()

    def get_time(self):
        """Returns the current time on this clock in secs (sub-ms precision)
        """
        return get_time() - self._start_time

    def getTime(self):
        """Alias get_time so we can set the default psychopy clock in logging.
        """
        return self.get_time()

    @property
    def start_time(self):
        return self._start_time


mono_clock = MonoClock()
