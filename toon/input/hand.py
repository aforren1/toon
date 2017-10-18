from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from builtins import super
from future import standard_library
standard_library.install_aliases()
import struct
import numpy as np
from toon.input.base_input import BaseInput
import hid

class Hand(BaseInput):
    """Interface to HAND.

    This provides an interface to HAND, which is developed by members of
    Kata and the BLAM Lab.

    """
    def __init__(self, nonblocking=True, **kwargs):
        """
        Args:
            nonblocking (bool): Whether the HID interface blocks for input.
        Notes:
        `nonblocking` should typically remain `True`, as I doubt there's any performance
        benefit and it leads to difficult debugging.

        Data is formatted as [x, y, z] per finger (15 elements, 3 per finger).

        Examples:
            Initialization should be straightforward.

            >>> device = Hand(nonblocking=True)
        """

        super(Hand, self).__init__(**kwargs)

        self._rotval = np.pi / 4.0
        self._sinval = np.sin(self._rotval)
        self._cosval = np.cos(self._rotval)
        self.nonblocking = nonblocking
        self._device = None
        self._data_buffer = np.full(15, np.nan)

    def __enter__(self):
        """HAND-specific initialization.
        """
        self._device = hid.device()
        for d in hid.enumerate():
            if d['product_id'] == 1158 and d['usage'] == 512:
                dev_path = d['path']
        self._device.open_path(dev_path)
        self._device.set_nonblocking(self.nonblocking)
        return self

    def read(self):
        """HAND-specific read function."""
        timestamp = self.time()
        data = self._device.read(46)
        if data:
            data = struct.unpack('>LhHHHHHHHHHHHHHHHHHHHH', bytearray(data))
            data = np.array(data, dtype='d')
            data[0] /= 1000.0  # device timestamp (since power-up, in milliseconds)
            data[2:] /= 65535.0
            self._data_buffer[0::3] = data[2::4] * self._cosval - data[3::4] * self._sinval  # x
            self._data_buffer[1::3] = data[2::4] * self._sinval + data[3::4] * self._cosval  # y
            self._data_buffer[2::3] = data[4::4] + data[5::4]  # z
            return {'time': timestamp, 'data': self._data_buffer,
                    'device_time': data[0], 'us_deviation': data[1]}
        return None

    def __exit__(self, type, value, traceback):
        """Close the HID interface."""
        self._device.close()
