import multiprocessing as mp
import ctypes
import copy
from numbers import Number
import numpy as np

class MultiprocessInput(object):
    """
    Manages the remote process and the various shared arrays.

    Called by the :func:`Input` factory function.
    """

    def __init__(self, device=None, **kwargs):
        nrow = kwargs.pop('nrow', 40)
        device_args = kwargs

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
        """Put locks on all data, copy data to the local process.

        Implementation note:
        We currently end up making an extra copy of the data, when we do the
        logical subsetting upon return. However, we *could* just find the first
        `np.nan`, and do a `0:N` slice, which creates a view instead. What I haven't
        figured out, though, is whether this will create unexpected behavior for the
        user (e.g. if they stuff the results of each `read()` in a list, and return to
        it later only to find all data is identical). We can encourage users to copy
        the data to some larger array (in which case I don't think future changes to the
        `_local_data_buffers` would carry over...).
        """

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
        # return non-nan timestamps and data
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
            # make more easily-accessible versions of the shared arrays
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
                        # find next row
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
                        else:  # replace oldest data with newest data
                            for ii in range(len(dev.data_dims)):
                                np_data_buffers[ii][:] = np.roll(np_data_buffers[ii], -1, axis=0)
                                np_data_buffers[ii][-1, :] = data[ii]
                            np_time_buffer[:] = np.roll(np_time_buffer, -1, axis=0)
                            np_time_buffer[-1, 0] = timestamp
                    # if the device always has data available, can rate-limit via this
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
