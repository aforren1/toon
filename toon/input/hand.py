import struct
import numpy as np
import hid
from toon.input.lsl_wrapper import BaseInput


class Hand(BaseInput):
    name = 'ToonHand'
    type = 'HAND'
    channel_count = 15

    def __init__(self, nonblocking=False, **kwargs):
        super(Hand, self).__init__(nominal_srate=1000.0,
                                   channel_format='float32',
                                   **kwargs)
        self._rot = np.pi / 4.0
        self._sinrot = np.sin(self._rot)
        self._cosrot = np.cos(self._rot)
        self.nonblocking = nonblocking
        self._device = None
        self._data_buffer = np.full(15, np.nan)

    def __enter__(self):
        super(Hand, self).__enter__()
        self._device = hid.device()
        for d in hid.enumerate():
            if d['product_id'] == 1158 and d['usage'] == 512:
                dev_path = d['path']
        self._device.open_path(dev_path)
        self._device.set_nonblocking(self.nonblocking)
        return self

    def __exit__(self, type, value, traceback):
        self._device.close()

    def read(self):
        data = self._device.read(46)
        time = self.time()
        if data:
            data = struct.unpack('>LhHHHHHHHHHHHHHHHHHHHH', bytearray(data))
            data = np.array(data, dtype='d')
            data[0] /= 1000.0
            data[2:] /= 65535.0
            self._data_buffer[0::3] = data[2::4] * self._cosrot - data[3::4] * self._sinrot  # x
            self._data_buffer[1::3] = data[2::4] * self._sinrot + data[3::4] * self._cosrot  # y
            self._data_buffer[2::3] = data[4::4] + data[5::4]  # z
            self.outlet.push_sample(self._data_buffer, time)
