import multiprocessing as mp
import multiprocessing.connection as conn
import threading as th
import gc
import psutil
conn.BUFSIZE = 2 ** 16 # up the size of the pipe buffer (for windows)


class MultiprocessInput(object):
    def __init__(self, device=None, priority='high',
                 disable_gc=True, _sampling_period=0):
        """
        Allows the user poll an input device without blocking the main process.
        Args:
            device: An input device that inherits from :class:`toon.input.BaseInput`.
            priority (string): Priority of the remote process. Either 'high' or 'norm'.
            disable_gc (bool): Switches off garbage collection on the remote process.
            _sampling_period (float): Only use if the input device constantly has its
                state available.
        """
        self._device = device
        # multiprocessing machinery
        self.local, self.remote = mp.Pipe(duplex=False)
        self.remote_ready = mp.Event()
        self.stop_remote = mp.Event()
        self._sampling_period = _sampling_period
        self._disable_gc = disable_gc
        self._priority = priority
        # local thread for reading
        self.stop_thread = th.Event()
        self.lock_thread = th.Lock()

    def __enter__(self):
        # remote process settings
        self.remote_ready.clear()
        self.stop_remote.clear()
        self._process = mp.Process(target=_mp_worker,
                                   args=(self.remote,
                                         self.remote_ready,
                                         self.stop_remote,
                                         self._device,
                                         self._disable_gc,
                                         self._sampling_period))
        self._process.daemon = True
        self._clear_pipe()
        self._process.start()
        self.remote_ready.wait()
        self._pid = self._process.pid
        self._proc = psutil.Process(self._pid)
        self._original_nice = self._proc.nice()
        self._set_priority(self._priority)

        # local reading thread settings
        self.stop_thread.clear()
        self._thread = th.Thread(target=self._read_pipe)
        self._thread.daemon = True
        self._thread.start()
        self._local_data = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._set_priority('norm')
        self.stop_remote.set() # stop remote polling process
        self.stop_thread.set() # stop local reading thread

    def read(self):
        """Read all pending data from the 'receiving' end of the multiprocessing Pipe."""
        with self.lock_thread:
            if len(self._local_data):
                data_copy = self._local_data[:]
                self._local_data[:] = []
                return data_copy
            return None

    def _read_pipe(self):
        """Read the pipe on a separate thread."""
        while not self.stop_thread.is_set():
            while self.local.poll():
                data = self.local.recv()
                with self.lock_thread:
                    self._local_data.append(data)

    def _clear_pipe(self):
        """Clear any pending data."""
        while self.local.poll():
            self.local.recv()

    def _set_priority(self, val):
        """Helper function to set priority. Inflexible."""
        try:
            if val == 'high':
                if psutil.WINDOWS:
                    self._proc.nice(psutil.HIGH_PRIORITY_CLASS)
                else:
                    self._proc.nice(-10)
            else:
                self._proc.nice(self._original_nice)
        except psutil.AccessDenied:
            pass # silently fails if not allowed to bump priority

def _mp_worker(remote, remote_ready, stop_remote, dev, disable_gc, sampling_period):
    """
    Function that runs on the remote process.
    Args:
        remote: The 'sending' end of the multiprocessing Pipe.
        remote_ready: Used to tell the original process that the remote is ready to sample.
        stop_remote: Used to tell the remote process to stop sampling.
    """
    if disable_gc:
        gc.disable()
    with dev:
        remote_ready.set()
        t0 = dev.time() + sampling_period  # first sampling period will be off
        while not stop_remote.is_set():
            data = dev.read()
            if data is not None:
                remote.send(data)
                while dev.time() < t0:
                    pass
                t0 = dev.time() + sampling_period