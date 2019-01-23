from ctypes import c_double

import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from nidaqmx.stream_readers import AnalogMultiChannelReader

from toon.input.device import BaseDevice, make_obs


class ForceKeyboard(BaseDevice):
    Forces = make_obs('Forces', (10,), c_double)

    sampling_frequency = 100

    def __init__(self, sampling_frequency=100, **kwargs):
        super(ForceKeyboard, self).__init__(**kwargs)
        self.sampling_frequency = sampling_frequency
        self.period = 1/self.sampling_frequency
        self.t1 = 0
        self._buffer = np.full(self.Forces.shape, np.nan)

    def enter(self):
        # assume first NI DAQ is the one we want
        self._device_name = nidaqmx.system.System.local().devices[0].name
        self._channels = [self._device_name + '/ai' + str(n) for n in
                          [2, 9, 1, 8, 0, 10, 3, 11, 4, 12]]
        self._device = nidaqmx.Task()
        self._device.ai_channels.add_ai_voltage_chan(
            ','.join(self._channels),
            terminal_config=TerminalConfiguration.RSE
        )
        self._reader = AnalogMultiChannelReader(self._device.in_stream)
        self._device.start()

    def read(self):
        self._reader.read_one_sample(self._buffer)
        time = self.clock()
        ret = self.Returns(forces=self.Forces(time, self._buffer))
        while self.clock() - t1 < self.period:
            pass
        self.t1 = self.clock()
        return ret

    def exit(self, *args):
        self._device.stop()
        self._device.close()
