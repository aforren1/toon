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

        if any(not isinstance(i, list) for i in data_dims):
            data_dims = [data_dims]

        self.data_dims = data_dims  # e.g. 5, [3,3] for 3x3 matrix, [5, [3,3]] for
                                    # two buffers -- one vector of length 5,
                                    # one 3x3 matrix
        # allocate single-line data buffers
        self._data_buffers = [np.full(dd, np.nan) for dd in data_dims]
        self.name = type(self).__name__


    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def read(self):
        """Return timestamp, data"""
        pass

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        pass


class MultiprocessInput(object):
        def __init__(self,
                     device=None,
                     nrow=None,
                     data_dims=None):
            # make all things nested equally, so iteration works later
            if any(not isinstance(i, list) for i in data_dims):
                data_dims = [data_dims]

            self._n_data_out = len(data_dims)
            self._device = device # swallow the original device (so we can use context managers)
            self._shared_lock = mp.Lock() # use a single lock for time, data
            self._mp_time_buffer = mp.Array(ctypes.c_double, nrow,
                                            lock=self._shared_lock)
            self._mp_data_buffers = [mp.Array(ctypes.c_double,
                                              int(np.prod(dd.append(nrow))),
                                              lock=self._shared_lock)
                                     for dd in data_dims]
            self._poison_pill = mp.Value(ctypes.c_bool) # has its own lock
            self._poison_pill.value = False
            self._process = None
            self._sampling_period = 0

            # user-friendly versions of the multiprocessing arrays.
            self._np_time_buffer = shared_to_numpy(self._mp_time_buffer,
                                                   (nrow, 1))
            # The first axis corresponds to time, others are data
            self._np_data_buffers = [shared_to_numpy(self._mp_data_buffers[i],
                                                     data_dims[i].insert(0, nrow))
                                     for i in range(self._n_data_out)]
            self._local_time_buffer = np.copy(self._np_time_buffer)
            self._local_data_buffers = [np.copy(d) for d in self._np_data_buffers]

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
                for i in range(len(self._local_data_buffers)):
                    np.copyto(self._local_data_buffers[i],
                              self._np_data_buffers)
                self._clear_remote_buffers()
                if np.isnan(self._local_time_buffer).all():
                    return None, [None * self._n_data_out]
            return self._local_time_buffer, self._local_data_buffers

        def _clear_remote_buffers(self):
            """Only called pre-multiprocess start, or when we already have the lock"""
            self._mp_time_buffer.fill(np.nan)
            for data in self._local_data_buffers:
                data.fill(np.nan)



def shared_to_numpy(mp_arr, dims):
    """Convert a :class:`multiprocessing.Array` to a numpy array.
    Helper function to allow use of a :class:`multiprocessing.Array` as a numpy array.
    Derived from the answer at:
    <https://stackoverflow.com/questions/7894791/use-numpy-array-in-shared-memory-for-multiprocessing>
    """
    return np.frombuffer(mp_arr.get_obj()).reshape(dims)
