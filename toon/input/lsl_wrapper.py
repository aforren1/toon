# What we want:
#
# If sampling a local device, spawn another process (via multiprocessing), and spin on that
# If sampling a remote device, assume that it exists already and start reading from it
# Have a standalone device class (minus LSL stuff)
import multiprocessing as mp
import abc
from pylsl import (StreamInfo, StreamOutlet, StreamInlet,
                   resolve_stream, local_clock)

class LslDevice(object):
    """
    Either pass in device or name/type/source id (and don't spawn device)

    kwargs are passed to the device"""
    def __init__(self, device=None, name='', type='', source_id='', **kwargs):
        self.flag = mp.Event()
        self.remote_ready = mp.Event()
        self.proc = None
        self._device = device
        self._device_args = kwargs
        self.name = name
        self.type = type
        self.source_id = source_id

    def __enter__(self):
        if self._device:
            self.flag.clear()
            self.remote_ready.clear()
            self.proc = mp.Process(target=self._worker, args=(self.flag, self.remote_ready))
            self.proc.daemon = True
            self.proc.start()
            self.remote_ready.wait()
            streams = resolve_stream('name', self._device.name,
                                     'type', self._device.type,
                                     'source_id', self._device.source_id)
        else:
            streams = resolve_stream('name', self.name,
                                     'type', self.type,
                                     'source_id', self.source_id)
        self.inlet = StreamInlet(streams[0])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.inlet.close_stream()
        if self._device:
            self.flag.set()

    def read(self):
        """Read multiple samples (returns (None, None) if nothing)
        TODO: Add time correction automatically (if LSL clock)?
        """
        return self.inlet.pull_chunk()

    def read_single(self):
        """Read single sample (returns (None, None) if nothing)"""
        return self.inlet.pull_sample(timeout=0.0)

    def _worker(self, flag, remote_ready):
        dev = self._device(self._device_args)
        with dev as d:
            remote_ready.set()
            while not flag.is_set():
                d.read()


class BaseInput(object):
    """
    Base class for devices compatible with :function:`Input`.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, clock_source=local_clock, name='', type='', source_id=''):
        """
        Args:
            clock_source: Clock or timer that returns the current (absolute or relative) time.
        """
        self.time = clock_source
        # TODO: enforce that these are set in derived classes
        self.name = name
        self.type = type
        self.source_id = source_id

    @abc.abstractmethod
    def __enter__(self):
        """Start communications with the device."""
        return self

    @abc.abstractmethod
    def read(self):
        """
        Call `self.outlet.push_sample(self._data_buffer, time)`
        """
        pass

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        """Place the device in a desirable state and close the connection (if required)."""
        pass
