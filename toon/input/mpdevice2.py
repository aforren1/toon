import ctypes
import multiprocessing as mp
import numpy as np
from sys import platform
# unconditional reuirement of numpy >= 1.16.1
from numpy.ctypeslib import as_ctypes_type

# numpy as front, multiprocessing array as backend
# time datatype is determined on-the-fly (just call timer fn)


def shared_to_numpy(mp_arr, dims):
    """Convert a :class:`multiprocessing.Array` to a numpy array.
    Helper function to allow use of a :class:`multiprocessing.Array` as a numpy array.
    Derived from the answer at:
    <https://stackoverflow.com/questions/7894791/use-numpy-array-in-shared-memory-for-multiprocessing>
    """
    return np.frombuffer(mp_arr, dtype=mp_arr._type_).reshape(dims)


class MpDevice(object):
    """Creates and manages a process for polling an input device."""

    def __init__(self, device, buffer_len=None):
        """Create a new MpDevice.

        Parameters
        ----------
        device: object (derived from toon.input.BaseDevice)
            Input device object.
        buffer_len: int, optional
            Overrides the device's sampling_frequency when specifing the size of the
            circular buffer.
        """
        self.device = device
        self.buffer_len = buffer_len

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
        # For Macs, use spawn (interaction with OpenGL or ??)
        # Windows only does spawn
        if platform == 'darwin' or platform == 'win32':
            mp.freeze_support()  # for Windows executable support
            try:
                mp.set_start_method('spawn')
            except (AttributeError, RuntimeError):
                pass  # already started a process, or on python2

        n_buffers = 2
        # make one lock per buffer
        self.shared_locks = [mp.Lock() for i in range(n_buffers)]
        self.remote_ready = mp.Event()  # signal to main process that remote is done setup
        self.kill_remote = mp.Event()  # signal to remote process to die
        self.local_err, remote_err = mp.Pipe(duplex=False)
        self.current_buffer_index = mp.Value(ctypes.c_bool, 0, lock=False)

        # figure out number of observations to save between reads
        nrow = 100  # default (100 Hz)
        # if we have a sampling_frequency, allocate 1s worth
        # should be enough wiggle room for 60Hz refresh rate
        if self.device.sampling_frequency:
            nrow = self.device.sampling_frequency
        if self.buffer_len:  # buffer_len overcomes all
            nrow = self.buffer_len
        nrow = int(max(nrow, 1))  # make sure we have at least one row

        # preallocate data
        # we have a double buffer sort of thing going on,
        # so we need two of everything
        self._data = []
        for i in range(n_buffers):
            # make mp version
            if self.device.shape == (1,):
                new_dim = (nrow,)
            else:
                new_dim = (nrow,) + self.device.shape
            flat_dim = np.product(new_dim)
            mp_arr = mp.Array(self.device.ctype, flat_dim, lock=False)
            np_arr = shared_to_numpy(mp_arr, new_dim)
