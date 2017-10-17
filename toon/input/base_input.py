import abc
import numpy as np
from time import time
from toon.input.mp_input import check_and_fix_dims

class BaseInput(object):
    """
    Base class for devices compatible with :function:`Input`.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, clock_source=time, data_dims=None):
        """
        Args:
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
