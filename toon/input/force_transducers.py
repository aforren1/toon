from ctypes import c_double
import numpy as np
from toon.input.base_input import BaseInput
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration


class ForceTransducers(BaseInput):
    """1-DoF force transducers."""

    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 200)

    @staticmethod
    def data_shapes(**kwargs):
        return [[10]]

    @staticmethod
    def data_types(**kwargs):
        return [c_double]

    def __init__(self, **kwargs):
        super(ForceTransducers, self).__init__(**kwargs)
        self.sampling_frequency = ForceTransducers.samp_freq(**kwargs)
        self._device_name = nidaqmx.system.System.local().devices[0].name  # assume first NI DAQ is the one we want
        self._channels = [self._device_name + '/ai' + str(n) for n in
                          [2, 9, 1, 8, 0, 10, 3, 11, 4, 12]]
        self.period = 1/self.sampling_frequency
        self.t1 = 0
        self._data_buffer = np.full(ForceTransducers.data_shapes(**kwargs)[0], np.nan)

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
        np.copyto(self._data_buffer, data)
        while self.clock() < self.t1:
            pass
        self.t1 = self.clock() + self.period
        return time, self._data_buffer

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._device.stop()
        self._device.close()
