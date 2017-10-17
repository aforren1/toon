import abc
import numpy as np
from time import time
from toon.input.mp_input import MultiprocessInput, check_and_fix_dims


def Input(device, mp=False, **kwargs):
    """
    Factory function to create input devices.

    Args:
        device:  class that inherits from :class:`BaseInput` (not an instance!).
        mp (bool): Whether device polling is done on a new process.
        **kwargs: Keyword arguments that are passed to the `device` constructor
            (and the :class:`MultiprocessInput` constructor, if `mp` is True.

            If `mp` is True, then the following \*\*kwargs are accepted:
                nrow (int): The number of rows used for the shared buffers; default is 40.
                sampling_period (float): Rate-limit polling the remote process, if state is
                    always available; default is 0 (spin as fast as possible).

    Returns:
        An input device, either an instantiation of the class passed in (`mp = False`) or
        a :class:`MultiproessInput` (`mp = True`), which will begin polling the device when
        the context manager is created.

    """
    if mp:
        return MultiprocessInput(device, **kwargs)
    return device(**kwargs)


class BaseInput(object):
    """
    Base class for devices compatible with :function:`Input`.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, **kwargs):
        """

        Args:
            **kwargs: Keyword arguments. At minimum, includes the following:
                clock_source: Clock or timer that returns the current (absolute or relative) time.
                data_dims: Either a single integer, a list containing a single integer, or a list of
                    lists, used to pre-allocate data outputted from the device.

                    Examples (good)::
                        3 # single vector of length 3
                        [3] # single vector of length 3
                        [[3], [2]] # two vectors, one of length 3 and the other of 2
                        [[3, 2]] # one 3x2 matrix
                        [[2,3], [5,4,3]] # one 2x3 matrix, one 5x4x3 array.
                    Examples (bad)::
                        [3,2] # ambiguous (two vectors or one matrix?)
                        [3, [3,2]] # not necessarily bad, but not currently handled
                        [[[3,2], 2], [5, 5]] # cannot handle deeper levels of nesting

        """
        clock_source = kwargs.get('clock_source', time)
        data_dims = kwargs.get('data_dims', None)

        if data_dims is None:
            raise ValueError('Must specify expected dimensions of data.')
        data_dims = check_and_fix_dims(data_dims)
        self.data_dims = data_dims

        # allocate data buffers
        self._data_buffers = [np.full(dd, np.nan) for dd in data_dims]
        self._data_elements = len(data_dims)
        self.name = type(self).__name__
        self.time = clock_source

    @abc.abstractmethod
    def __enter__(self):
        """Start communications with the device."""
        return self

    @abc.abstractmethod
    def read(self):
        """
        Return the timestamp, and either a single piece of data or
        multiple pieces of data (as a list).

        Examples:
            return timestamp, data
            return timestamp, [data1, data2]
        """
        pass

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        """Place the device in a desirable state and close the connection (if required)."""
        pass
