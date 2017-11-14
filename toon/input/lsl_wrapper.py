# What we want:
#
# If sampling a local device, spawn another process (via multiprocessing), and spin on that
# If sampling a remote device, assume that it exists already and start reading from it
# Have a standalone device class (minus LSL stuff)
import multiprocessing as mp
import abc
from pylsl import (StreamInfo, StreamOutlet, StreamInlet,
                   resolve_stream, local_clock, IRREGULAR_RATE)

class LslDevice(object):
    """
    Either pass in device or name/type/source id (and don't spawn device)

    kwargs are passed to the device"""
    def __init__(self, device=None, name='default', type='', source_id='', **kwargs):
        self.flag = mp.Event()
        self.remote_ready = mp.Event()
        self.proc = None
        self._device = device
        self._device_args = kwargs
        self.name = name
        self.type = type
        self.source_id = source_id

    def __enter__(self):
        """
        If the device is specified (i.e. local), then spawn a new process and
        poll the device on that.

        Otherwise, assume the device is already spitting data out elsewhere,
        and just read chunks continuously.

        TODO: Check if we need to handle metadata
        """
        if self._device:
            self.flag.clear()
            self.remote_ready.clear()
            self.proc = mp.Process(target=self._worker,
                                   args=(self.flag,
                                         self.remote_ready,
                                         self._device,
                                         self.source_id,
                                         self._device_args))
            self.proc.daemon = True
            self.proc.start()
            self.remote_ready.wait()
            streams = resolve_stream('source_id', self.source_id)
        else:
            streams = resolve_stream('source_id', self.source_id)
        self.inlet = StreamInlet(streams[0])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.inlet.close_stream()
        self.inlet = None
        self.flag.set()

    def read(self):
        """Read multiple samples (returns (None, None) if nothing)
        TODO: Add time correction automatically (if LSL clock)?
        """
        return self.inlet.pull_chunk()

    def read_single(self):
        """Read single sample (returns (None, None) if nothing)"""
        return self.inlet.pull_sample(timeout=0.0)

    @staticmethod
    def _worker(flag, remote_ready, device, source_id, device_args):
        """This method does the grunt work on the remote process."""
        dev = device(source_id=source_id, **device_args)
        with dev as d:
            remote_ready.set()
            while not flag.is_set():
                d.read() # read data from the device


class BaseInput(object):
    """
    Base class for devices.

    NOTE: This currently assumes a single stream from a single device.
    What about multiple streams from a single device?
    """
    __metaclass__ = abc.ABCMeta

    # TODO: I think this construct is only valid in python 3?
    @property
    @abc.abstractmethod
    def name(self):
        """Name of the stream."""
        pass

    @property
    @abc.abstractmethod
    def type(self):
        """Content of the stream, e.g. EEG, ..."""
        pass

    @property
    @abc.abstractmethod
    def channel_count(self):
        """Number of elements in a single channel."""
        pass


    @abc.abstractmethod
    def __init__(self,
                 clock_source=local_clock,
                 source_id='',
                 nominal_srate=IRREGULAR_RATE,
                 channel_format='float32'):
        """
        Args:
            clock_source: Clock or timer that returns the current (absolute or relative) time.
        """
        self.time = clock_source
        self.source_id = source_id # unique! so need to set in instantiation
        self.nominal_srate = nominal_srate
        self.channel_format = channel_format

    @abc.abstractmethod
    def __enter__(self):
        """Start communications with the device."""
        self.info = StreamInfo(self.name, self.type,
                               self.channel_count,
                               self.nominal_srate,
                               self.channel_format,
                               self.source_id)
        self.outlet = StreamOutlet(self.info)

    @abc.abstractmethod
    def read(self):
        """
        Call `self.outlet.push_sample(data, time)` at the end
        """
        pass

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        """Place the device in a desirable state and close the connection (if required)."""
        pass
