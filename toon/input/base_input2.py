import abc
import multiprocessing as mp
import ctypes
import numpy as np


class BaseInput(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 clock_source=None,
                 data_dims=None):
        """data_dims is list or list of lists"""

        if data_dims is None:
            raise ValueError('Must specify expected dimensions of data.')

        self.data_dims = data_dims  # e.g. 5 for a vector of length 5, [3,3] for 3x3 matrix, [5, [3,3]] for
        # two buffers -- one vector of length 5,
        #  one 3x3 matrix

        # allocate single-line data buffers
        # if there's only a single dimension, use a vector
        # for multiple dimensions, use a list
        if not isinstance(data_dims, list):
            self._data_buffers = np.full(data_dims, np.nan)
            self._data_elements = 1  # how many pieces of data we return
        else:
            self._data_buffers = [np.full(dd, np.nan) for dd in data_dims]
            self._data_elements = len(data_dims)
        self.name = type(self).__name__

    @abc.abstractmethod
    def __enter__(self):
        """Start comms with device"""
        pass

    @abc.abstractmethod
    def read(self):
        """Return timestamp, data"""
        pass

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        """Put the device in a proper state"""
        pass


class MultiprocessInput(object):
    def __init__(self,
                 device=None,
                 nrow=None,
                 data_dims=None):

        if not isinstance(device, BaseInput):
            raise ValueError('Device must inherit from BaseInput.')

        self._device = device  # swallow the original device (so we can use context managers)
        self._shared_lock = mp.Lock()  # use a single lock for time, data

        # allocate data
        # The first axis corresponds to time, others are data
        if self._device._data_elements == 1:
            self._data_buffer_dims = data_dims.insert(0, nrow)
            self._mp_data_buffers = mp.Array(ctypes.c_double,
                                             int(np.prod(self._data_buffer_dims)),
                                             lock=self._shared_lock)
            self._np_data_buffers = shared_to_numpy(self._mp_data_buffers,
                                                    self._data_buffer_dims)
            self._local_data_buffers = np.copy(self._np_data_buffers)
        else:  # more than one piece of data from a device, data_buffers becomes a list
            self._data_buffer_dims = [dd.insert(0, nrow) for dd in data_dims]
            self._mp_data_buffers = [mp.Array(ctypes.c_double,
                                              int(np.prod(dd)),
                                              lock=self._shared_lock)
                                     for dd in self._data_buffer_dims]
            self._np_data_buffers = [shared_to_numpy(self._mp_data_buffers[i],
                                                     self._data_buffer_dims[i])
                                     for i in range(self._device._data_elements)]
            self._local_data_buffers = [np.copy(d) for d in self._np_data_buffers]

        # timestamp containers
        self._mp_time_buffer = mp.Array(ctypes.c_double, nrow,
                                        lock=self._shared_lock)
        self._np_time_buffer = shared_to_numpy(self._mp_time_buffer,
                                               (nrow, 1))
        self._local_time_buffer = np.copy(self._np_time_buffer)

        self._poison_pill = mp.Value(ctypes.c_bool)  # has its own lock
        self._poison_pill.value = False
        self._process = None
        self._sampling_period = 0  # set if the device always returns data, not necessarily new
        self._no_data = None if self._device._data_elements == 1 else [None] * self._device._data_elements
        self._nrow = nrow
        self._data_dims = data_dims

    def __enter__(self):
        self._poison_pill.value = False
        self._process = mp.Process(target=self._mp_worker,
                                   args=(self._device,
                                         self._poison_pill,
                                         self._shared_lock,
                                         self._mp_time_buffer,
                                         self._mp_data_buffers))
        self._clear_remote_buffers()
        self._process.start()
        return self

    def __exit__(self, type, value, traceback):
        with self._shared_lock:
            self._poison_pill.value = True
        self._process.join()

    def read(self):
        """Put locks on all data, copy across"""
        # we can just use the single lock, because they all share the same one
        with self._mp_time_buffer.get_lock():
            np.copyto(self._local_time_buffer, self._np_time_buffer)
            if not isinstance(self._np_data_buffers, list):
                np.copyto(self._local_data_buffers,
                          self._np_data_buffers)
            else:
                for i in range(len(self._local_data_buffers)):
                    np.copyto(self._local_data_buffers[i],
                              self._np_data_buffers)
            self._clear_remote_buffers()
            if np.isnan(self._local_time_buffer).all():
                return None, self._no_data
        return self._local_time_buffer, self._local_data_buffers

    def _clear_remote_buffers(self):
        """Only called pre-multiprocess start, or when we already have the lock"""
        self._mp_time_buffer.fill(np.nan)
        if not isinstance(self._np_data_buffers, list):
            self._local_data_buffers.fill(np.nan)
        else:
            for data in self._local_data_buffers:
                data.fill(np.nan)

    def _mp_worker(self, device,
                   poison_pill, shared_lock,
                   mp_time_buffer, mp_data_buffers):
        with device as dev:
            self._clear_remote_buffers()
            np_time_buffer = shared_to_numpy(mp_time_buffer, (self._nrow, 1))
            if not isinstance(mp_data_buffers, list):
                np_data_buffers = shared_to_numpy(mp_data_buffers,
                                                  self._data_buffer_dims)
            else:
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
                    with mp_time_buffer.get_lock():
                        # first handle the single-data case:
                        if not isinstance(np_data_buffers, list):
                            current_nans = np.isnan(np_data_buffers).any(axis=1)
                            if current_nans.any():
                                next_index = np.where(current_nans)[0][0]
                                np_data_buffers[next_index, :] = data
                                np_time_buffer[next_index, 0] = timestamp
                            else:
                                np_data_buffers[:] = np.roll(np_data_buffers, -1, axis=0)
                                np_time_buffer[:] = np.roll(np_time_buffer, -1, axis=0)
                                np_data_buffers[-1, :] = data
                                np_time_buffer[-1, 0] = timestamp
                        # handle the multi-data case
                        else:
                            current_nans = np.isnan(np_data_buffers[0]).any(axis=1)
                            if current_nans.any():
                                next_index = np.where(current_nans)[0][0]
                                for ii in range(len(dev._data_elements)):
                                    np_data_buffers[ii][next_index, :] = data[ii]
                                np_time_buffer[next_index, 0] = timestamp
                            else:
                                for ii in range(len(dev._data_elements)):
                                    np_data_buffers[ii][:] = np.roll(np_data_buffers[ii], -1, axis=0)
                                    np_data_buffers[ii][-1, :] = data
                                np_time_buffer[:] = np.roll(np_time_buffer, -1, axis=0)
                                np_time_buffer[-1, 0] = timestamp
                    while (dev.time() - t0) <= self._sampling_period:
                        pass


def shared_to_numpy(mp_arr, dims):
    """Convert a :class:`multiprocessing.Array` to a numpy array.
    Helper function to allow use of a :class:`multiprocessing.Array` as a numpy array.
    Derived from the answer at:
    <https://stackoverflow.com/questions/7894791/use-numpy-array-in-shared-memory-for-multiprocessing>
    """
    return np.frombuffer(mp_arr.get_obj()).reshape(dims)
