import multiprocessing as mp
import gc
import psutil

class MultiprocessInput(object):
    def __init__(self, device=None, _sampling_period=0,
                 disable_gc=False, priority='normal'):
        """
        Allows the user poll an input device without blocking the main process.
        Args:
            device: An input device that inherits from :class:`toon.input.BaseInput`.
            _sampling_period (float): Only use if the input device constantly has its
                state available.
        """
        self._device = device
        self.local, self.remote = mp.Pipe(duplex=False)
        self.remote_ready = mp.Event()
        self.stop_remote = mp.Event()
        self._sampling_period = _sampling_period
        self._disable_gc = disable_gc
        self._priority = priority

    def __enter__(self):
        self.remote_ready.clear()
        self.stop_remote.clear()
        self._process = mp.Process(target=self._mp_worker,
                                   args=(self.remote,
                                         self.remote_ready,
                                         self.stop_remote))
        self._process.daemon = True
        self._clear_pipe()
        self._process.start()
        self.remote_ready.wait()
        self._pid = self._process.pid
        self._proc = psutil.Process(self._pid)
        self._original_nice = self._proc.nice()
        self.set_priority('high')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.set_priority('norm')
        self.stop_remote.set()

    def read(self):
        """Read all pending data from the 'receiving' end of the multiprocessing Pipe."""
        data = list()
        while self.local.poll():
            data.append(self.local.recv())
        if data:
            return data
        return None

    def _mp_worker(self, remote, remote_ready, stop_remote):
        """
        Function that runs on the remote process.
        Args:
            remote: The 'sending' end of the multiprocessing Pipe.
            remote_ready: Used to tell the original process that the remote is ready to sample.
            stop_remote: Used to tell the remote process to stop sampling.

        """
        if self._disable_gc:
            gc.disable()
        with self._device as dev:
            remote_ready.set()
            t0 = dev.time() + self._sampling_period  # first sampling period will be off
            while not stop_remote.is_set():
                data = dev.read()
                if data is not None:
                    remote.send(data)
                    while dev.time() < t0:
                        pass
                t0 = dev.time() + self._sampling_period

    def _clear_pipe(self):
        """Clear any pending data."""
        while self.local.poll():
            self.local.recv()

    def set_priority(self, val):

        try:
            if val == 'high':
                if psutil.WINDOWS:
                    self._proc.nice(psutil.HIGH_PRIORITY_CLASS)
                else:
                    self._proc.nice(-10)
            else:
                self._proc.nice(self._original_nice)
        except psutil.AccessDenied:
            pass
