from ctypes import c_double

import numpy as np

import hid
import usb.core
import usb.util
from toon.input.device import BaseDevice, Obs


class Hand(BaseDevice):
    sampling_frequency = 1000

    class Pos(Obs):
        shape = (15,)
        ctype = c_double

    def __init__(self, blocking=True, **kwargs):
        super(Hand, self).__init__(**kwargs)
        self._sqrt2 = np.sqrt(2)
        self._device = None
        self._buffer = np.full(15, np.nan)
        self.blocking = blocking

    def __enter__(self):
        self._device = hid.device()
        # TODO: we may have different endpoints, make more robust?
        self._device.open(0x16c0, 0x486)
        self._device.set_nonblocking(not self.blocking)
        return self

    def __exit__(self):
        self._device.close()

    def read(self):
        data = self._device.read(46)
        time = self.clock()
        # timestamp, deviation from period, and 20x16-bit analog channels
        data = struct.unpack('>Lh' + 'H' * 20, bytearray(data))
        data = np.array(data, dtype='d')
        data[2:] /= 65535.0
        data[2:] -= 0.5
        self._buffer[0::3] = (data[2::4] - data[3::4])/self._sqrt2
        self._buffer[1::3] = (data[2::4] + data[3::4])/self._sqrt2
        self._buffer[2::3] = data[4::4] + data[5::4]
        return self.Returns(self.Pos(time, data))


# USB demo (should be phenotypically identical to above)
class UsbHand(BaseDevice):
    sampling_frequency = 1000

    class Pos(Obs):
        shape = (15,)
        ctype = c_double

    def __init__(self, **kwargs):
        super(UsbHand, self).__init__(**kwargs)
        self._sqrt2 = np.sqrt(2)
        self._device = None
        self._buffer = np.full(15, np.nan)

    def __enter__(self):
        dev = usb.core.find(idVendor=0x16c0, idProduct=0x486)
        if dev is None:
            raise ValueError('Device not found.')
        # there was definitely more to claiming the device,
        # but I can't find the ref now
        self.ep_in = dev[0][(0, 0)][0]  # get the proper endpoint
        return self

    def __exit__(self):
        pass  # nothing to do?

    def read(self):
        data = self.ep_in.read(self.ep_in.wMaxPacketSize)
        time = self.clock()
        data = struct.unpack('>Lh' + 'H'  20, data[:46])
        data = np.array(data, dtype='d')
        data[2:] /= 65535.0
        data[2:] -= 0.5
        self._buffer[0::3] = (data[2::4] - data[3::4])/self._sqrt2
        self._buffer[1::3] = (data[2::4] + data[3::4])/self._sqrt2
        self._buffer[2::3] = data[4::4] + data[5::4]
        return self.Returns(self.Pos(time, data))
