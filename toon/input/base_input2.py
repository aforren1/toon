import abc
import multiprocessing as mp
import ctypes
import numpy as np
from time import time
import copy
from numbers import Number


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


class MultiprocessInput(object):
    """
    Manages the remote process and the various shared arrays.

    Called by the :func:`Input` factory function.
    """

    def __init__(self, device=None, **kwargs):
        nrow = kwargs.pop('nrow', 40)
        device_args = kwargs
        if not issubclass(device, BaseInput):
            raise ValueError('Device must inherit from BaseInput.')

        self._device = device  # swallow the original device (so we can use context managers)
        self._shared_lock = mp.RLock()  # use a single lock for time, data

        self._device_args = copy.deepcopy(device_args)
        # pull out the data dimensions so we can preallocate the necessary arrays
        data_dims = check_and_fix_dims(device_args['data_dims'])
        num_data = len(data_dims)

        # allocate data
        # The first axis corresponds to time, others are data
        self._data_buffer_dims = data_dims
        for dd in self._data_buffer_dims:
            dd.insert(0, nrow)
        # the "raw" version
        self._mp_data_buffers = [mp.Array(ctypes.c_double,
                                          int(np.prod(dd)),
                                          lock=self._shared_lock)
                                 for dd in self._data_buffer_dims]
        # this is the same data as _mp_data_buffers, but easier to manipulate
        self._np_data_buffers = [shared_to_numpy(self._mp_data_buffers[i],
                                                 self._data_buffer_dims[i])
                                 for i in range(num_data)]
        for dd in self._np_data_buffers:
            dd.fill(np.nan)
        # this is the data we'll manipulate on the main process (copied from _np_data_buffers)
        self._local_data_buffers = [np.copy(d) for d in self._np_data_buffers]

        # timestamp containers (same logic as data)
        self._mp_time_buffer = mp.Array(ctypes.c_double, nrow,
                                        lock=self._shared_lock)
        self._np_time_buffer = shared_to_numpy(self._mp_time_buffer,
                                               (nrow, 1))
        self._np_time_buffer.fill(np.nan)
        self._local_time_buffer = np.copy(self._np_time_buffer)

        # _poison_pill ends the remote process
        self._poison_pill = mp.Value(ctypes.c_bool)  # has its own lock
        self._poison_pill.value = False
        self._process = None  # where our multiprocess.Process lands
        # in single-data-element case, don't return a list
        self._no_data = None if num_data == 1 else [None] * num_data
        self._nrow = nrow
        self._num_data = num_data
        # only devices that constantly have data available might need this,
        # squirreled it away because it may be confusing to users
        self._sampling_period = kwargs.get('sampling_period', 0)

    def __enter__(self):
        """Start the remote process."""
        self._poison_pill.value = False
        self._process = mp.Process(target=self._mp_worker,
                                   args=(self._poison_pill,
                                         self._shared_lock,
                                         self._mp_time_buffer,
                                         self._mp_data_buffers))
        self._clear_remote_buffers()
        self._process.start()
        return self

    def __exit__(self, type, value, traceback):
        """Signal to the remote process to finish."""
        with self._poison_pill.get_lock():
            self._poison_pill.value = True
        self._process.join()

    def read(self):
        """Put locks on all data, copy data to the local process."""

        # we can just use the single lock, because they all share the same one
        with self._shared_lock:
            np.copyto(self._local_time_buffer, self._np_time_buffer)
            for i in range(len(self._local_data_buffers)):
                np.copyto(self._local_data_buffers[i],
                          self._np_data_buffers[i])
        self._clear_remote_buffers()
        if np.isnan(self._local_time_buffer).all():
            return None, self._no_data
        dims = [tuple(range(-1, -len(dd.shape), -1)) for dd in self._local_data_buffers]
        time = self._local_time_buffer[~np.isnan(self._local_time_buffer).any(axis=1)]
        # special case: if only one piece of data, remove from list
        if self._num_data == 1:
            data = self._local_data_buffers[0][~np.isnan(self._local_data_buffers[0]).any(axis=dims[0])]
        else:
            data = [self._local_data_buffers[i][~np.isnan(self._local_data_buffers[i]).any(axis=dims[i])]
                    for i in range(len(self._local_data_buffers))]
        return time, data

    def _clear_remote_buffers(self):
        """Reset the shared arrays.

        This is only called once we have acquired the lock.
        """
        self._np_time_buffer.fill(np.nan)
        for data in self._np_data_buffers:
            data.fill(np.nan)

    def _mp_worker(self, poison_pill, shared_lock,
                   mp_time_buffer, mp_data_buffers):
        """

        Args:
            poison_pill: Shared boolean, signals the end of the remote process.
            shared_lock: Common lock, used by the timestamp array and all data arrays.
            mp_time_buffer: 1-dimensional array that stores timestamp information.
            mp_data_buffers: N-dimensional array of data or list of N-dimensional arrays.

        """
        # create a new instance of the device
        device = self._device(**self._device_args)
        with device as dev:
            self._clear_remote_buffers()
            np_time_buffer = shared_to_numpy(mp_time_buffer, (self._nrow, 1))
            np_data_buffers = [shared_to_numpy(mp_data_buffers[i],
                                               self._data_buffer_dims[i])
                               for i in range(dev._data_elements)]
            stop_sampling = False
            while not stop_sampling:
                t0 = dev.time()
                with poison_pill.get_lock():
                    stop_sampling = poison_pill.value
                timestamp, data = dev.read()
                if timestamp is not None:
                    with shared_lock:
                        current_nans = np.isnan(np_time_buffer).any(axis=1)
                        if current_nans.any():
                            next_index = np.where(current_nans)[0][0]
                            # handle single element of data
                            if isinstance(data, list):
                                for ii in range(len(dev.data_dims)):
                                    np_data_buffers[ii][next_index, :] = data[ii]
                            else:
                                np_data_buffers[0][next_index, :] = data
                            np_time_buffer[next_index, 0] = timestamp
                        else:
                            for ii in range(len(dev.data_dims)):
                                np_data_buffers[ii][:] = np.roll(np_data_buffers[ii], -1, axis=0)
                                np_data_buffers[ii][-1, :] = data[ii]
                            np_time_buffer[:] = np.roll(np_time_buffer, -1, axis=0)
                            np_time_buffer[-1, 0] = timestamp
                    # if the device always has data, can rate-limit via this
                    while (dev.time() - t0) <= self._sampling_period:
                        pass


def shared_to_numpy(mp_arr, dims):
    """Convert a :class:`multiprocessing.Array` to a numpy array.
    Helper function to allow use of a :class:`multiprocessing.Array` as a numpy array.
    Derived from the answer at:
    <https://stackoverflow.com/questions/7894791/use-numpy-array-in-shared-memory-for-multiprocessing>
    """
    return np.frombuffer(mp_arr.get_obj()).reshape(dims)


def check_and_fix_dims(input):
    """
    Helper function to ensure data dimensions are consistent and unambiguous.

    Args:
        input: Scalar, list, or list of lists.

    Returns:
        List of lists.
    """
    # handle special-case, single scalar
    if isinstance(input, Number):
        input = [[input]]
    elif isinstance(input, (list, tuple, np.ndarray)):
        # special-case num 2, where we have a single scalar in a list
        if len(input) == 1 and isinstance(input[0], Number):
            input = [input]
        elif len(input) != 1 and any([isinstance(x, Number) for x in input]):
            raise ValueError('Ambiguous dimensions. There should be one list per expected piece of data' + \
                             ' from the input device.')
        # coerce array-like things to lists
        input = [list(x) for x in input]
        # now we're relatively comfortable we have a list of lists
    else:
        raise ValueError('Something is wrong with the input.')
    return input
