import platform
from time import time
import numpy as np
from toon.input.base_input import DummyTime

if platform.system() is 'Windows':
    import nidaqmx
    import nidaqmx.system
    from nidaqmx.constants import AcquisitionType
    from nidaqmx.stream_readers import AnalogMultiChannelReader
    from nidaqmx.utils import flatten_channel_string
    system = nidaqmx.system.System.local()
else:
    raise NotImplementedError('NIDAQ only available on Windows.')

class ForceTransducers(nidaqmx.Task):
    """1D transducers."""

    def __init__(self,
                 clock_source=DummyTime):
        super(nidaqmx.Task, self).__init__()
        self.time = clock_source
        self._device = 'Dev1'  # figure out programmatically, e.g. system[0]?
        self._channels = [self._device + '/' + str(n) for n in
                          [2, 9, 1, 8, 0, 10, 3, 11, 4, 12]]
        self._buffer = np.full((40, 10), np.nan, dtype='float64')
        self._out_buffer = np.full((40, 10), np.nan, dtype='float64')


    def __enter__(self):

        self._start_time = self.time.getTime()
        self.timing.cfg_samp_clk_timing(200, sample_mode=AcquisitionType.CONTINUOUS)

        self.ai_channels.add_ai_voltage_chan(
            flatten_channel_string(self._channels),
            max_val=10, min_val=-10
        )
        self._reader = AnalogMultiChannelReader(self.in_stream)
        self.start()

    def read(self):
        self._reader.read_many_sample(self._buffer, )
        return np.copyto(self._out_buffer, self._buffer)

