import ctypes
import multiprocessing as mp
import os
from collections import namedtuple
from sys import platform

import numpy as np
from numpy.ctypeslib import as_ctypes_type
from psutil import pid_exists

from toon.input._tbprocess import Process
from toon.util import priority

ret = namedtuple('mpdata', ['time', 'data'])
noneret = ret(None, None)


def shared_to_numpy(mp_arr, dims):
    """Convert a :class:`multiprocessing.Array` to a numpy array.
    Helper function to allow use of a :class:`multiprocessing.Array` as a numpy array.
    Derived from the answer at:
    <https://stackoverflow.com/questions/7894791/use-numpy-array-in-shared-memory-for-multiprocessing>
    """
    return np.frombuffer(mp_arr, dtype=mp_arr._type_).reshape(dims)


class MpDevice(object):
    """Creates and manages a process for polling an input device."""

    def __init__(self, device, buffer_len=None, use_views=False):
        """Create a new MpDevice.

        Parameters
        ----------
        device: object (derived from toon.input.BaseDevice)
            Input device object.
        buffer_len: int, optional
            Overrides the device's sampling_frequency when specifing the size of the
            circular buffer.
        use_views: bool, optional
            Return views (False by default; faster, but more error-prone) or copy data returned by `read()`.
        """
        if device.ctype is None:
            raise RuntimeError('Device ctype must be set.')

        self.device = device
        self.buffer_len = buffer_len
        self._use_views = use_views
        self.process = None
        # For Macs, use spawn (interaction with OpenGL or ??)
        # Windows only does spawn
        if platform in ['darwin', 'win32']:
            mp.freeze_support()  # for Windows executable support
            try:
                mp.set_start_method('spawn')
            except (AttributeError, RuntimeError):
                pass  # already started a process, or on python2

        self.remote_ready = mp.Event()  # signal to main process that remote is done setup
        self.kill_remote = mp.Event()  # signal to remote process to die
        self.current_buf_index = mp.RawValue(ctypes.c_uint64, 0)
        self.prev_buf_index = 0

        # figure out number of observations to save between reads
        nrow = 500  # default (500 Hz)
        # if we have a sampling_frequency, allocate 1s worth
        # should be enough wiggle room for 60Hz refresh rate
        if self.device.sampling_frequency:
            nrow = self.device.sampling_frequency
        if self.buffer_len:  # buffer_len overcomes all
            nrow = self.buffer_len
        nrow = int(max(nrow, 10))  # make sure we have at least ten rows
        self._nrow = nrow

        # preallocate data
        # we have a double buffer sort of thing going on,
        # so we need two of everything
        self._data = []
        time_type = as_ctypes_type(type(self.device.clock()))
        # make mp version
        is_scalar = False
        if self.device.shape == (1,):
            new_dim = (nrow,)
            is_scalar = True
        else:
            new_dim = (nrow,) + self.device.shape
        flat_dim = int(np.product(new_dim))
        ctype = self.device.ctype
        # Structures get padding when passing through this,
        # so only run on non-Structures
        if isinstance(ctype, list):
            ctype = as_ctypes_type(ctype)
            globals()['struct'] = ctype
        elif not issubclass(ctype, ctypes.Structure):
            ctype = as_ctypes_type(ctype)
        mp_arr = mp.RawArray(ctype, flat_dim)
        np_arr = shared_to_numpy(mp_arr, new_dim)
        t_mp_arr = mp.RawArray(time_type, nrow)
        t_np_arr = shared_to_numpy(t_mp_arr, nrow)
        # generate local version
        local_arr = np.empty_like(np_arr)
        t_local_arr = np.empty_like(t_np_arr)
        if is_scalar:
            local_arr = np.squeeze(local_arr)
        # special case for buffer size of 1 and scalar data
        if local_arr.shape == ():
            local_arr.shape = (1,)
        self._data = {'mp_data': mp_arr, 'np_data': np_arr,
                      'mp_time': t_mp_arr, 'np_time': t_np_arr}

        # make local versions to copy the data into
        self._local_arr = local_arr
        self._t_local_arr = t_local_arr
        self.device.local = True

    def start(self):
        """Start polling from the device on the child process.
        Allocates all resources and creates the child process.

        Notes
        -----
        Prefer using as a context manager over explicitly starting and stopping.

        Raises
        ------
        Will raise an exception if something goes wrong during instantiation
        of the device.
        """
        if not self.device.local:
            raise RuntimeError('MpDevice is already started.')

        self.process = Process(target=remote,
                               kwargs={'dev': self.device,
                                       'data': self._data,
                                       'remote_ready': self.remote_ready,
                                       'kill_remote': self.kill_remote,
                                       'parent_pid': os.getpid(),
                                       'current_buf_index': self.current_buf_index})

        self.process.daemon = True
        self.process.start()
        self.check_error()
        self.remote_ready.wait()  # block until child process is ready
        self.device.local = False  # try to prevent local access to the device
        self.prev_buf_index = 0
        self.current_buf_index.value = 0

    def read(self):
        """Retrieve all observations that have occurred since the last read.
        Notes
        -----
        The data is stored in a circular buffer, which means that if the number
        of observations since the last read exceeds the preallocated data, the oldest
        data will be overwritten in favor of the newest. If this behavior is undesirable,
        either bump the sampling_frequency of the Device or the buffer_len of the MpDevice
        up to an adequate number, depending on the sampling rate of the device and how
        often you expect to call read().
        We copy data by default. If `use_views` is set to True upon initialization,
        then *views* are returned, which is faster (but more error prone).

        Returns
        -------
        Named tuple (time, data), or None if there is no data.

        Raises
        ------
        May raise an exception if one has occurred on the child process since the last read.
        """
        self.check_error()
        nr = self._nrow
        # wrap counter at nrow
        prev_buf_index = self.prev_buf_index % nr
        current_buf_index = self.current_buf_index.value % nr
        diff = current_buf_index - prev_buf_index
        # if no new samples (or traversed the entirety of the buffer),
        # short circuit (should we error/warn if the latter?)
        if diff == 0:
            return None

        self.prev_buf_index = self.current_buf_index.value
        data = self._data
        # working up the array
        if diff > 0:
            # slice enough to hold the interval from prev to current
            length = diff
        else:  # rolled over the end of the array
            # TODO: check check check
            length = nr - prev_buf_index + current_buf_index

        # TODO: check if length > self._nrow?
        # start writing from the top of the array
        t_out = self._t_local_arr[:length]
        data_out = self._local_arr[:length]
        np_data = data['np_data']
        np_time = data['np_time']
        if diff > 0:
            data_out[:] = np_data[prev_buf_index:current_buf_index]
            t_out[:] = np_time[prev_buf_index:current_buf_index]
        else:
            # two copies: one to end, one from beginning
            idx1 = nr - prev_buf_index
            data_out[:idx1] = np_data[prev_buf_index:]
            data_out[idx1:] = np_data[:current_buf_index]
            t_out[:idx1] = np_time[prev_buf_index:]
            t_out[idx1:] = np_time[:current_buf_index]

        # return time, data views (fast)
        if self._use_views:
            return ret(t_out, data_out)
        # otherwise, return copies
        return ret(np.copy(t_out), np.copy(data_out))

    def clear(self):
        """Discard all pending observations."""
        self.check_error()
        self.prev_buf_index = self.current_buf_index.value

    def check_error(self):
        """See if any exceptions have occurred on the child process, or whether
        the device was already closed.
        """
        if self.process:
            if not self.process.is_alive():
                if self.process.exception:
                    err, traceback = self.process.exception
                    raise err
                else:
                    raise RuntimeError('MpDevice is closed.')
        else:
            raise RuntimeError('MpDevice has not been started yet.')

    def stop(self):
        """Stop reading from the device and kill the child process.
        Notes
        -----
        Prefer using as a context manager over explicitly starting and stopping.
        """
        self.kill_remote.set()
        self.process.join(timeout=1)
        self.device.local = True
        self.kill_remote.clear()
        self.remote_ready.clear()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


def process_data(shared_time, shared_data, local_time, local_data, shared_counter, is_struct, nrow):
    next_index = shared_counter.value % nrow
    if is_struct:
        # np.ctypeslib.as_array is ~30x slower?
        local_data = np.frombuffer(local_data, dtype=shared_data.dtype)
    shared_time[next_index] = local_time
    shared_data[next_index] = local_data
    shared_counter.value += 1


def remote(dev, data, remote_ready, kill_remote, parent_pid, current_buf_index):
    # from timeit import default_timer
    # need to re-generate connection between mp and np arrays
    dims = data['np_data'].shape
    np_data = shared_to_numpy(data['mp_data'], dims)
    np_time = shared_to_numpy(data['mp_time'], dims[0])
    is_struct = np_data.dtype.type == np.void
    nr = dims[0]
    try:
        priority(1)  # high priority (non-realtime, though) and disables gc
        with dev:
            remote_ready.set()  # signal all set to the parent process
            while not kill_remote.is_set() and pid_exists(parent_pid):
                # either a (time, data) tuple or list of (time, data) tuples
                # or None if nothing
                device_dat = dev.read()
                # t0 = default_timer()
                if device_dat is None:
                    continue  # next read

                if isinstance(device_dat, list):
                    for dat in device_dat:
                        process_data(np_time, np_data, dat[0], dat[1],
                                     current_buf_index, is_struct, nr)
                else:
                    process_data(np_time, np_data, device_dat[0], device_dat[1],
                                 current_buf_index, is_struct, nr)
                # print(default_timer() - t0)

    finally:
        priority(0)
        remote_ready.set()
