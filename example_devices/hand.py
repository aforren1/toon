from ctypes import c_double
import platform
import struct
import numpy as np

import hid
import usb.core
import usb.util
from toon.input.device import BaseDevice


def get_teensy_path(serial_number):
    hids = hid.enumerate()
    hids = [h for h in hids if h['product_id'] == 0x486 and h['vendor_id'] == 0x16c0]
    # if we have a serial number, filter on that too
    # otherwise, we'll end up taking the first
    if serial_number:
        hids = [h for h in hids if h['serial_number'] == serial_number]
    system = platform.system()
    if system == 'Darwin':
        hid_path = next(h['path'] for h in hids if h['usage'] == 512)
    elif system in ('Windows', 'Linux'):
        hid_path = next(h['path'] for h in hids if h['interface_number'] == 0)
    return hid_path


class Hand(BaseDevice):
    sampling_frequency = 1000
    ctype = c_double
    shape = (15,)

    def __init__(self, serial_number=None, blocking=True, **kwargs):
        super(Hand, self).__init__(**kwargs)
        self._inv_sqrt2 = 1/np.sqrt(2)
        self._device = None
        self._buffer = np.full(15, np.nan)
        self.serial_number = serial_number
        self.blocking = blocking

    def enter(self):
        self._device = hid.device()
        self._device.open_path(get_teensy_path(self.serial_number))
        self._device.set_nonblocking(not self.blocking)

    def exit(self):
        self._device.close()

    def read(self):
        data = self._device.read(46)
        time = self.clock()
        # timestamp, deviation from period, and 20x16-bit analog channels
        data = struct.unpack('>Lh' + 'H' * 20, bytearray(data))
        data = np.array(data, dtype='d')
        data[2:] /= 65535.0
        data[2:] -= 0.5
        self._buffer[0::3] = (data[2::4] - data[3::4]) * self._inv_sqrt2
        self._buffer[1::3] = (data[2::4] + data[3::4]) * self._inv_sqrt2
        self._buffer[2::3] = data[4::4] + data[5::4]
        return time, self._buffer
