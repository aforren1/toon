import abc
from time import time

class BaseInput(object):
    """
    Base class for devices compatible with :function:`Input`.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, clock_source=time):
        """
        Args:
            clock_source: Clock or timer that returns the current (absolute or relative) time.
        """
        self.name = type(self).__name__
        self.time = clock_source

    @abc.abstractmethod
    def __enter__(self):
        """Start communications with the device."""
        return self

    @abc.abstractmethod
    def read(self):
        """
        Return the data as a dictionary, e.g. {'timestamp': time, 'data': data}.
        All shapes and sizes allowed.
        """
        pass

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        """Place the device in a desirable state and close the connection (if required)."""
        pass
