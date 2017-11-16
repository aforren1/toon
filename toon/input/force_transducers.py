import numpy as np
from toon.input.lsl_wrapper import BaseInput

import nidaqmx
import nidaqmx.system
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
system = nidaqmx.system.System.local()


class ForceTransducers(BaseInput):
    """1D transducers."""
    name = 'ToonTransducers'
    type = 'ForceTransducers'
    channel_count = 10

    def __init__(self, **kwargs):
        super(ForceTransducers, self).__init__(nominal_srate=200, **kwargs)
        self._device_name = system.devices[0].name  # Assume the first NIDAQ-mx device is the one we want
        self._channels = [self._device_name + '/ai' + str(n) for n in
                          [2, 9, 1, 8, 0, 10, 3, 11, 4, 12]]

    def __enter__(self):
        super(ForceTransducers, self).__enter__()
        self._device = nidaqmx.Task()
        self._device.ai_channels.add_ai_voltage_chan(
            ','.join(self._channels),
            terminal_config=TerminalConfiguration.RSE
        )
        self._device.timing.cfg_samp_clk_timing(200, sample_mode=AcquisitionType.CONTINUOUS,
                                                samps_per_chan=2)

        def callback(task_handle, every_n_samples_type, number_of_samples, callback_data):
            ts = self.time()
            samples = self._device.read(number_of_samples_per_channel=2)
            self.outlet.push_sample([s[0] for s in samples], ts)
            self.outlet.push_sample([s[1] for s in samples], ts)
            return 0

        self._device.register_every_n_samples_acquired_into_buffer_event(2, callback)
        self._device.start()
        return self

    def read(self):
        pass

    def __exit__(self, type, value, traceback):
        self._device.stop()
        self._device.close()
