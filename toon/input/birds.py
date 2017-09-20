import struct
import time
import numpy as np
import serial
from toon.input.base_input import BaseInput, DummyTime


class BlamBirds(BaseInput):
    def __init__(self, clock_source=DummyTime(),
                 multiprocess=False,
                 buffer_rows=10,
                 ports=None,
                 master=None,
                 data_mode='position'):

        if master not in ports:
            raise ValueError('The master must be named amongst the ports.')
        if data_mode not in ['position']:
            raise ValueError('Invalid or unimplemented data mode.')
        _ncol = 3 * len(ports)
        super(BlamBirds, self).__init__(clock_source, multiprocess, buffer_rows, _ncol)
        self._birds = None
        self.ports = ports
        self.master = master
        self._master_index = ports.index(master)
        self.data_mode = data_mode
        self._bird_data = np.full(self._ncol, np.nan)  # fill with bird data later

    def _init_device(self):
        self._birds = [serial.Serial(port, baudrate=115200,
                                     bytesize=serial.EIGHTBITS,
                                     xonxoff=0,
                                     rtscts=0,
                                     timeout=0.001)
                       for port in self.ports]
        for bird in self._birds:
            bird.setRTS(0)

        # init master
        # fbb auto config
        time.sleep(1)
        self._birds[self._master_index].write(('P' + chr(0x32) + chr(len(self.ports))).encode('UTF-8'))
        time.sleep(1)
        self._birds[self._master_index].write(b'P' + b'\x07' + struct.pack('<H', int(130 * 256)))

        for bird in self._birds:
            # position as output data type
            bird.write(b'V')
            # change Vm table to Ascension's "snappy" settings
            bird.write(b'P' + b'\x0C' + struct.pack('<HHHHHHH', *[2, 2, 2, 10, 10, 40, 200]))
            # first 5 bits are meaningless, B2 is 0 (AC narrow ON), B1 is 1 (AC wide OFF), B0 is 0 (DC ON)
            bird.write(b'P' + b'\x04' + b'\x02' + b'\x00')

        for bird in self._birds:
            bird.write(b'@')  # 'stream' command

    def start(self):
        super(BlamBirds, self).start()

    def _read(self):
        timestamp = self.time.getTime()
        _datalist = list()
        for bird in self._birds:
            _datalist.append(bird.read(6))  # assumes position data
        # don't convert if data not there
        if not any(b'' == s for s in _datalist):
            _datalist = [self.decode(msg) for msg in _datalist]
            data = np.array(_datalist).reshape((6,))  # assumes position data
            data[:] = data[[1, 2, 0, 4, 5, 3]]  # reorder
            # rotate
            tmp_x = data[::3]
            tmp_y = data[1::3]
            data[::3] = tmp_x * np.cos(-0.01938) - tmp_y * np.sin(-0.01938)
            data[1::3] = tmp_y * np.sin(-0.01938) + tmp_y * np.cos(-0.01938)

            # translate
            data[::3] += 61.35
            data[1::3] += 17.69
            return data, timestamp
        return None, None

    def read(self):
        data, timestamp = super(BlamBirds, self).read()
        return data, timestamp

    def clear(self):
        super(BlamBirds, self).clear()

    def stop(self):
        super(BlamBirds, self).stop()

    def close(self):
        super(BlamBirds, self).close()

    def _stop_device(self):
        for bird in self._birds:
            bird.write(b'?')  # stop stream

    def _close_device(self):
        self._birds[self._master_index].write(b'G')  # sleep (master only?)
        for bird in self._birds:
            bird.close()

    def _mp_worker(self, *args):
        super(BlamBirds, self)._mp_worker(*args)

    def decode(self, msg, n_words=3):
        return [self._decode_words(msg, i) for i in range(int(n_words))]

    def _decode_words(self, s, i):
        v = self._decode_word(s[2 * i:2 * i + 2])
        v *= 36 * 2.54  # scaling to cm
        return v / 32768.0

    def _decode_word(self, msg):
        lsb = msg[0] & 0x7f
        msb = msg[1]
        v = (msb << 9) | (lsb << 2)
        if v < 0x8000:
            return v
        return v - 0x10000
