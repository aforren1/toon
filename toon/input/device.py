import abc
from toon.util import mono_clock


def prevent_if_remote(func):
    """Decorator to raise ValueError in order to prevent accidental use
    of a remote device locally.
    """
    def wrap_if_remote(*args, **kwargs):
        self = args[0]
        if self._local:
            return func(*args, **kwargs)
        raise ValueError('Device is being used on a remote process.')
    return wrap_if_remote


class BaseDevice(metaclass=abc.ABCMeta):
    """Abstract base class for input devices.
    Attributes
    ----------
    sampling_frequency: int
        Expected sampling frequency of the device, used by toon.input.MpDevice for preallocation.
        We preallocate for 1 second of data (e.g. 500 samples for a sampling_frequency of 500 Hz).

    Notes
    -----
    The user supplies `enter` and `exit`, not the dunder methods (`__enter__`, `__exit__`).
    """
    sampling_frequency = 500
    shape = (1,)  # shape can technically be None, but
    ctype = None  # ctype must be present

    def __init__(self, clock=mono_clock.get_time):
        """Create new device.
        Parameters
        ----------
        clock: function or method
            The clock used for timestamping events. Defaults to toon.input.mono_clock, which
            allows us to share a reference time between the parent and child processes. The 
            mono_clock is based off psychopy.clock.MonotonicClock 
            (on Windows, time.perf_counter seems to be relative to when the process is created, 
            which makes it difficult to relate the time between processes).

        Notes
        -----

        Do not start communicating with the device in `__init__`, wait until `enter()`.
        """
        self._local = True  # MpDevice toggles this in the main process
        self.clock = clock

    @abc.abstractmethod
    def read(self):
        pass

    def enter(self):
        # we separate enter and exit from the dunder methods
        # so inheriting classes need not use the decorator
        pass

    def exit(self):
        pass

    @prevent_if_remote
    def __enter__(self):
        self.enter()
        return self

    @prevent_if_remote
    def __exit__(self, *args):
        self.exit()

    @property
    def local(self):
        return self._local

    @local.setter
    def local(self, val):
        self._local = bool(val)
