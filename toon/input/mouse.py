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
        self.win = False
        if win is not None:
            self.win = True
            self.winunits = win.units
            self.winsize = win.size
            self.winwidth = win.monitor.getWidth()
            self.winsizepix = win.monitor.getSizePix()[0]

    def _init_device(self):
        import mouse
        self._device = mouse

    def _read(self):
        """Conversions from psychopy"""
        timestamp = self.time.getTime()
        self._buffer[:] = self._device.get_position()
        self._buffer -= (self.winsize / 2)
        self._buffer[1] *= -1
        if self.win:
            if self.winunits == 'pix':
                pass
            elif self.winunits == 'norm':
                self._buffer *= 2.0 / self.winsize
            elif self.winunits == 'cm':
                self._buffer *= self.winwidth / self.winsizepix
            elif self.winunits == 'height':
                self._buffer /= float(self.winsize[1])
        return self._buffer, timestamp

    def _stop_device(self):
        pass
    def _close_device(self):
        pass
