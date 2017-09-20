import abc
from time import time
import multiprocessing as mp
import ctypes
import numpy as np


def shared_to_numpy(mp_arr, nrow, ncol):
    """Helper to allow use of a multiprocessing.Array as a numpy array"""
    return np.frombuffer(mp_arr.get_obj()).reshape((nrow, ncol))

class DummyTime(object):
    """Stand-in for
    from psychopy.core import monotonicClock as mc
    mc.getTime()
    """
    def getTime(self):
        return time()

class BaseInput(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 clock_source=DummyTime,
                 multiprocess=False,
                 buffer_rows=50,
                 _ncol=1):

        self.time = clock_source
        self.multiprocess = multiprocess
        self._start_time = None
        self._nrow = buffer_rows
        self._ncol = _ncol
        self._stopped = False

        if multiprocess:
            self._shared_mp_buffer = mp.Array(ctypes.c_double, self._nrow * self._ncol)
            self._shared_np_buffer = shared_to_numpy(self._shared_mp_buffer, self._nrow, self._ncol)
            self._shared_np_buffer.fill(np.nan)

            self._shared_mp_time_buffer = mp.Array(ctypes.c_double, self._nrow)
            self._shared_np_time_buffer = shared_to_numpy(self._shared_mp_time_buffer,
                                                          self._nrow,
                                                          1)
            self._shared_np_time_buffer.fill(np.nan)

            self._read_buffer = np.full((self._nrow, self._ncol), np.nan)
            self._read_time_buffer = np.full((self._nrow, 1), np.nan)
            self._poison_pill = mp.Value(ctypes.c_bool)
            self._poison_pill.value = True
            self._process = None

    @abc.abstractmethod
    def start(self):
        self._stopped = False
        self._start_time = self.time.getTime()
        if self.multiprocess:
            self._poison_pill.value = True
            self._process = mp.Process(target=self._mp_worker,
                                       args=(self._shared_mp_buffer,
                                             self._shared_mp_time_buffer,
                                             self._poison_pill))
            self._process.daemon = True
            self._process.start()
        else:  # start device on original processor
            self._init_device()

    @abc.abstractmethod
    def stop(self):
        """
        Stop reading, but possible to restart
        """
        self._stopped = True
        if self.multiprocess:
            self._poison_pill.value = False # also causes remote device to *close*
        else:
            self._stop_device()

    @abc.abstractmethod
    def close(self):
        """Deallocate device resources,
           make sure stop() is called first
        """
        if not self._stopped:
            self.stop()
        if not self.multiprocess:
            self._close_device()


    @abc.abstractmethod
    def read(self):
        """Return None if no data"""
        if self.multiprocess:
            with self._shared_mp_buffer.get_lock(), self._shared_mp_time_buffer.get_lock():
                np.copyto(self._read_buffer, self._shared_np_buffer)
                np.copyto(self._read_time_buffer, self._shared_np_time_buffer)
            self.clear()
            if np.isnan(self._read_buffer).all():
                return None, None
            return (self._read_buffer[~np.isnan(self._read_buffer).any(axis=1)],
                    self._read_time_buffer[~np.isnan(self._read_time_buffer).any(axis=1)])
        # no multiprocessing (returns tuple (data, timestamp))
        return self._read()

    @abc.abstractmethod
    def _read(self):
        """Core read method
        Read a single line (assumes vector is outcome)
        Return data, timestamp as separate!
        """
        return 0, 0

    @abc.abstractmethod
    def clear(self):
        """Remove all pending data (call read a few times?)"""
        if self.multiprocess:
            with self._shared_mp_buffer.get_lock(), self._shared_mp_time_buffer.get_lock():
                self._shared_np_buffer.fill(np.nan)
                self._shared_np_time_buffer.fill(np.nan)

    @abc.abstractmethod
    def _init_device(self):
        """Start talking to the actual device"""
        pass

    def _stop_device(self):
        """Clean-up (without disconnecting from device)"""
        pass

    @abc.abstractmethod
    def _close_device(self):
        """Disconnect from device"""
        pass

    @abc.abstractmethod
    def _mp_worker(self, shared_mp_buffer, shared_mp_time_buffer, poison_pill):
        """Poll device on separate process"""
        self._init_device()
        self.clear()  # purge buffers (in case there's residual stuff from previous run)
        shared_np_buffer = shared_to_numpy(shared_mp_buffer, self._nrow, self._ncol)
        shared_np_time_buffer = shared_to_numpy(shared_mp_time_buffer, self._nrow, 1)
        while poison_pill.value:
            data, timestamp = self._read()
            if data is not None:
                with shared_mp_buffer.get_lock(), shared_mp_time_buffer.get_lock():
                    current_nans = np.isnan(shared_np_buffer).any(axis=1)
                    if current_nans.any():
                        # fill in the next nan row
                        next_index = np.where(current_nans)[0][0]
                        shared_np_buffer[next_index, :] = data
                        shared_np_time_buffer[next_index, 0] = timestamp
                    else:
                        # replace the oldest data in the buffer with new data
                        shared_np_buffer[:] = np.roll(shared_np_buffer, -1, axis=0)
                        shared_np_time_buffer[:] = np.roll(shared_np_time_buffer, -1, axis=0)
                        shared_np_buffer[-1, :] = data
                        shared_np_time_buffer[-1, 0] = timestamp
        # call extra cleanup
        self._stop_device()
        self._close_device()
