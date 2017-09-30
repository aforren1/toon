import numpy as np
from toon.input.base_input import BaseInput, DummyTime

class Mouse(BaseInput):
    def __init__(self,
                 clock_source=DummyTime,
                 multiprocess=True,
                 nrow=10,
                 win=None):
        BaseInput.__init__(self, clock_source, multiprocess, (nrow, 2))
        self._buffer = np.full(2, np.nan)
        self._sampling_period = 0.01
        self.win = win

    def _init_device(self):
        import mouse
        self._device = mouse

    def _read(self):
        """Conversions from psychopy"""
        timestamp = self.time.getTime()
        self._buffer[:] = self._device.get_position()
        if self.win is not None:
            if self.win.units == 'pix':
                pass
            elif self.win.units == 'norm':
                self._buffer *= 2.0 / self.win.size
            elif self.win.units == 'cm':
                self._buffer *= self.win.getWidth() / self.win.getSizePix()[0]
            elif self.win.units == 'height':
                self._buffer /= float(self.win.size[1])
        return self._buffer, timestamp

    def _stop_device(self):
        pass
    def _close_device(self):
        pass
