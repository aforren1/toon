import struct
import time
from ctypes import c_double

import numpy as np
import serial

from toon.input.device import BaseDevice, Obs

# reference (most recent):
# https://github.com/aforren1/toon/blob/455d06827082ae30ec4ae3b2605185cb4d291c92/toon/input/birds.py


class BlamBirds(BaseDevice):
    class LeftPos(Obs):
        # x,y,z
        shape = (3,)
        ctype = ctypes.c_double

    class RightPos(Obs):
        shape = (3,)
        ctype = ctypes.c_double

    def __init__(self, ports=None, master=None, **kwargs):
        if not ports:
            raise ValueError('Must specify serial ports to use.')
        if not master:
            master = ports[0]
        if master not in ports:
            raise ValueError('Master must be listed amongst the ports.')
        self.ports = ports
        self.master = master
        self._birds = None
        self._master = None
        self.cos_const = np.cos(-0.01938)
        self.sin_const = np.sin(0.01938)
        super(BlamBirds, self).__init__(**kwargs)

    def __enter__(self):
        # timeout set so that we should always have data available
        self._birds = [serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS,
                                     xonxoff=0, rtscts=0, timeout=0.02) for port in self.ports]

        for bird in self._birds:
            bird.setRTS(0)
        self._master = [x for x in self._birds if x.port == self.master][0]
        # init master, FBB autoconfig
        time.sleep(1)
        self._master.write(('P' + chr(0x32) + chr(len(self.ports))).encode('utf-8'))
        time.sleep(1)
        # set the sampling frequency
        self._master.write(b'P' + b'\x07' + struct.pack('<H', int(130 * 256)))

        for bird in self._birds:
            # change output type to position
            bird.write(b'V')
            # change Vm table to Ascension's "snappy" settings
            bird.write(b'P' + b'\x0C' + struct.pack('<HHHHHHH', *[2, 2, 2, 10, 10, 40, 200]))
            # first 5 bits are meaningless, B2 is 0 (AC narrow ON), B1 is 1 (AC wide OFF), B0 is 0 (DC ON)
            bird.write(b'P' + b'\x04' + b'\x02' + b'\x01')

        # ready to go, start streaming from all birds
        for b in self._birds:
            b.write(b'@')
        return self

    def read(self):
        lst = []
        while not self._birds[0].in_waiting:
            pass
        time = self.clock()
        for bird in self._birds:
            lst.append(bird.read(6))  # assumes position data
        lst = [decode(msg) for msg in lst]
        data = np.array(lst).reshape((6,))  # position data for 2 birds
        data[:] = data[[1, 2, 0, 4, 5, 3]]  # fiddle with order of axes
        # rotate
        tmp_x = data[::3]
        tmp_y = data[1::3]
        data[::3] = tmp_x * self.cos_const - tmp_y * self.sin_const
        data[1::3] = tmp_y * self.sin_const + tmp_y * self.cos_const

        # translate
        data[::3] += 61.35
        data[1::3] += 17.69
        return self.Returns(self.Pos1(time, data[:3]), self.Pos2(time, data[3:]))


def __exit__(self, *args):
    for bird in self._birds:
        bird.write(b'?')  # stop stream
    self._master.write(b'G')  # sleep (master only?)
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
    import serial
    dev = MpDevice(BlamBirds, ports=['/dev/ttyUSB0', '/dev/ttyUSB1', ])
