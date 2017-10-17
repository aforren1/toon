import platform
from toon.input.base_input import BaseInput

if platform.system() is 'Windows':
    import nidaqmx
    import nidaqmx.system
    from nidaqmx.constants import AcquisitionType, TerminalConfiguration
    from nidaqmx.stream_readers import AnalogMultiChannelReader
    from nidaqmx.errors import DaqError

    system = nidaqmx.system.System.local()
else:
    raise NotImplementedError('NIDAQ only available on Windows.')


class ForceTransducers(BaseInput):
    """1D transducers."""

    def __init__(self, **kwargs):

        BaseInput.__init__(self, data_dims=10, **kwargs)

        self._device_name = system.devices[0].name  # Assume the first NIDAQ-mx device is the one we want
        self._channels = [self._device_name + '/ai' + str(n) for n in
                          [2, 9, 1, 8, 0, 10, 3, 11, 4, 12]]

    def __enter__(self):
        self._device = nidaqmx.Task()
        self._start_time = self.time.getTime()

        self._device.ai_channels.add_ai_voltage_chan(
            ','.join(self._channels),
            terminal_config=TerminalConfiguration.RSE
        )

        self._device.timing.cfg_samp_clk_timing(200, sample_mode=AcquisitionType.CONTINUOUS)
        self._reader = AnalogMultiChannelReader(self._device.in_stream)
        self._device.start()
        return self

    def read(self):
        timestamp = self.time()
        try:
            self._reader.read_one_sample(self._data_buffers[0], timeout=0)
        except DaqError:
            return None, None
        return timestamp, self._data_buffers[0]

    def __exit__(self, type, value, traceback):
        self._device.stop()
        self._device.close()
