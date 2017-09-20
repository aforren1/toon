import struct
import numpy as np
from toon.input.base_input import BaseInput, DummyTime
import hid

class Hand(BaseInput):
    def __init__(self, clock_source=DummyTime(),
                 multiprocess=False,
                 buffer_rows=50,
                 nonblocking=True,
                 _ncol=15):

        super(Hand, self).__init__(clock_source, multiprocess, buffer_rows, _ncol)

        self._rotval = np.pi/4.0
        self._sinval = np.sin(self._rotval)
        self._cosval = np.cos(self._rotval)
        self.nonblocking = nonblocking
        self._force_data = np.full(self._ncol, np.nan)
        self._device = None

    def _init_device(self):
        self._device = hid.device()
        self._device.open(0x16c0, 0x486)
        self._device.set_nonblocking(self.nonblocking)

    def _read(self):
        timestamp = self.time.getTime()
        data = self._device.read(46)
        if data:
            data = struct.unpack('>LhHHHHHHHHHHHHHHHHHHHH', bytearray(data))
            data = np.array(data, dtype='d')
            data[0] /= 1000.0
            data[1:] /= 65535.0
            self._force_data[0::3] = data[2::4] * self._cosval - data[3::4] * self._sinval  # x
            self._force_data[1::3] = data[2::4] * self._sinval + data[3::4] * self._cosval  # y
            self._force_data[2::3] = data[4::4] + data[5::4]  # z
            return self._force_data, timestamp
        return None, None

    def read(self):
        data, timestamp = super(Hand, self).read()
        return data, timestamp

    def clear(self):
        super(Hand, self).clear()

    def start(self):
        super(Hand, self).start()

    def stop(self):
        super(Hand, self).stop()

    def close(self):
        super(Hand, self).close()
        if not self.multiprocess:
            self._close_device() # close local device

    def _stop_device(self):
        super(Hand, self)._stop_device()

    def _close_device(self):
        self._device.close()

    def _mp_worker(self, *args):
        super(Hand, self)._mp_worker(*args)


