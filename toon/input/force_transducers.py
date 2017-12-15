from ctypes import c_double
import numpy as np
from toon.input.base_input import BaseInput
import nidaqmx
import nidaqmx.system
from nidaqmx.constants import AcquisitionType, TerminalConfiguration

system = nidaqmx.system.System.local()


class ForceTransducers(BaseInput):
    """1D transducers."""

    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 200)

    @staticmethod
    def data_shapes(**kwargs):
        return [[10]]

    @staticmethod
    def data_types(**kwargs):
        return [c_double]

    def __init__(self, sampling_frequency=200, **kwargs):
        super(ForceTransducers, self).__init__(sampling_frequency=sampling_frequency, **kwargs)
        self._device_name = system.devices[0].name  # Assume the first NIDAQ-mx device is the one we want
        self._channels = [self._device_name + '/ai' + str(n) for n in
                          [2, 9, 1, 8, 0, 10, 3, 11, 4, 12]]
        self.period = 1/sampling_frequency
        self.t1 = 0

    def __enter__(self):
        self._device = nidaqmx.Task()
        self._device.ai_channels.add_ai_voltage_chan(
            ','.join(self._channels),
            terminal_config=TerminalConfiguration.RSE
        )
        self._device.timing.cfg_samp_clk_timing(self.sampling_frequency,
                                                sample_mode=AcquisitionType.CONTINUOUS,
                                                samps_per_chan=1)
        self._device.start()
        return self

    def read(self):
        data = self._device.read()
        time = self.clock()
        while self.clock() < self.t1:
            pass
        self.t1 = self.clock() + self.period
        return time, np.copy(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._device.stop()
        self._device.close()
