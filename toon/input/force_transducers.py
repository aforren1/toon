import platform
import numpy as np
from toon.input.base_input import BaseInput, DummyTime

if platform.system() is 'Windows':
    import nidaqmx
    import nidaqmx.system
    from nidaqmx.constants import AcquisitionType
    from nidaqmx.stream_readers import AnalogMultiChannelReader
    from nidaqmx.utils import flatten_channel_string
    from nidaqmx.errors import DaqError

    system = nidaqmx.system.System.local()
else:
    raise NotImplementedError('NIDAQ only available on Windows.')


class ForceTransducers(BaseInput):
    """1D transducers."""

    def __init__(self,
                 clock_source=DummyTime,
                 multiprocess=False,
                 dims=(50, 10)):

        BaseInput.__init__(self, clock_source=clock_source,
                           multiprocess=multiprocess,
                           dims=dims)

        self._device_name = system.devices[0].name  # Assume the first NIDAQ-mx device is the one we want
        self._channels = [self._device_name + '/ai' + str(n) for n in
                          [2, 9, 1, 8, 0, 10, 3, 11, 4, 12]]
        self._small_buffer = np.full(dims[1], np.nan)

    def _init_device(self):
        self._device = nidaqmx.Task()
        self._start_time = self.time.getTime()

        self._device.ai_channels.add_ai_voltage_chan(
            flatten_channel_string(self._channels),
            max_val=10, min_val=-10
        )

        self._device.timing.cfg_samp_clk_timing(200, sample_mode=AcquisitionType.CONTINUOUS)
        self._reader = AnalogMultiChannelReader(self._device.in_stream)
        self._device.start()

    def _read(self):
        timestamp = self.time.getTime()
        try:
            self._reader.read_one_sample(self._small_buffer, timeout=0)
        except DaqError:
            return None, None
        return self._small_buffer, timestamp

    def _stop_device(self):
        self._device.stop()

    def _close_device(self):
        self._device.close()
