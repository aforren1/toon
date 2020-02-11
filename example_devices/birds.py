import struct
import time
from ctypes import c_double, Structure

import numpy as np
import serial
from serial.tools import list_ports

from toon.input.device import BaseDevice

# reference (most recent):
# https://github.com/aforren1/toon/blob/455d06827082ae30ec4ae3b2605185cb4d291c92/toon/input/birds.py

# with two birds, we can also try putting it in group mode & get adequate data rates


class Point3D(Structure):
    _fields_ = [('x', c_double), ('y', c_double), ('z', c_double)]


class BirdData(Structure):
    _fields_ = [('left', Point3D), ('right', Point3D)]


class Birds(BaseDevice):
    shape = (1,)
    ctype = BirdData

    def __init__(self, **kwargs):
        self._birds = None
        self._master = None
        self.indices = [1, 3]
        self.read_from = []
        self.cos_const = np.cos(-0.01938)
        self.sin_const = np.sin(0.01938)
        super(Birds, self).__init__(**kwargs)

    def enter(self):
        # timeout set so that we should always have data available
        devices = [x.device for x in list_ports.comports() if 'Keyspan' in x.description]
        self._birds = [serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS,
                                     xonxoff=0, rtscts=0, timeout=0.05) for port in devices]

        for bird in self._birds:
            bird.reset_input_buffer()
            bird.reset_output_buffer()
            bird.write(b'?')  # stop stream

        for bird in self._birds:
            bird.write(b'G')

        time.sleep(1)
        for bird in self._birds:
            bird.setRTS(0)

        # reorder birds
        out = [0 for i in range(len(self._birds))]
        for b in self._birds:
            b.write(b'\x4F' + b'\x15')
            res = b.read()
            res = struct.unpack('b', res)[0]
            out[res] = b
            if res == 1:
                self._master = b
        if self._master is None:
            raise ValueError('Master not found in ports provided.')
        self._birds = out  # overwrite unsorted
        # subset of birds to read
        for b in self._birds:
            if self.indices and res in self.indices:
                self.read_from.append(b)
        self.read_from.reverse()  # TODO: fix it up so that read_from is in order of bird indices
        # init master, FBB autoconfig
        time.sleep(1)
        self._master.write(('P' + chr(0x32) + chr(len(devices))).encode('utf-8'))
        time.sleep(3)

        # set the sampling frequency
        self._master.write(b'P' + b'\x07' + struct.pack('<H', int(130 * 256)))
        # check the sampling frequency
        # self._master.write(b'\x4F' + b'\x07')
        # time.sleep(0.1)
        # res = self._master.read(2)
        # print(struct.unpack('<H', res)[0]/256)

        for bird in self._birds:
            # change output type to position
            bird.write(b'V')
            # change Vm table to Ascension's "snappy" settings
            bird.write(b'P' + b'\x0C' + struct.pack('<HHHHHHH', *[2, 2, 2, 10, 10, 40, 200]))
            # first 5 bits are meaningless, B2 is 0 (AC narrow ON), B1 is 1 (AC wide OFF), B0 is 0 (DC ON)
            bird.write(b'P' + b'\x04' + b'\x02' + b'\x01')

        # ready to go, start streaming from birds whose indices were provided
        time.sleep(0.5)
        for b in self.read_from:
            b.write(b'@')

    def read(self):
        lst = []
        # busy wait until first byte available
        while not self.read_from[0].in_waiting:
            pass
        time = self.clock()
        for bird in self.read_from:
            lst.append(bird.read(6))  # assumes position data
        lst = [decode(msg) for msg in lst]
        data = np.array(lst).reshape((6,))  # position data for two birds
        data[:] = data[[1, 2, 0, 4, 5, 3]]  # fiddle with order of axes
        # rotate
        tmp_x = data[::3]
        tmp_y = data[1::3]
        data[::3] = tmp_x * self.cos_const - tmp_y * self.sin_const
        data[1::3] = tmp_y * self.sin_const + tmp_y * self.cos_const

        # translate to the lower left corner
        data[::3] += 61.35
        data[1::3] += 17.69
        out = BirdData(left=Point3D(*data[0:3]), right=Point3D(*data[3:6]))
        return time, out

    def exit(self):
        for bird in self.read_from:
            bird.write(b'?')  # stop stream
        time.sleep(1)
        self._master.write(b'G')  # sleep (master only?)
        time.sleep(1)
        for bird in self._birds:
            bird.close()


def decode(msg, n_words=3):
    return [decode_words(msg, i) for i in range(int(n_words))]


def decode_words(s, i):
    v = decode_word(s[2*i:2*i + 2])
    v *= 36 * 2.54  # scaling to cm
    return v / 32768.0


def decode_word(msg):
    lsb = msg[0] & 0x7f
    msb = msg[1]
    v = (msb << 9) | (lsb << 2)
    if v < 0x8000:
        return v
    return v - 0x10000


if __name__ == '__main__':
    import time
    from toon.input.mpdevice import MpDevice
    dev = MpDevice(Birds())
    times = []
    with dev:
        start = time.time()
        while time.time() - start < 20:
            dat = dev.read()
            if dat is not None:
                time, data = dat
                print(data['left'])
                times.append(np.diff(time))
            time.sleep(0.016)

    import matplotlib.pyplot as plt
    plt.plot(np.hstack(times))
    plt.show()
