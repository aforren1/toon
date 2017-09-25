"""
.. module:: input
     :platform: Unix, Windows
     :synopsis: Tools for dealing with input devices.

.. moduleauthor:: Alexander Forrence <aforren1@jhu.edu>

"""
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from builtins import super
from builtins import chr
from builtins import int
from builtins import range
from future import standard_library
standard_library.install_aliases()
import struct
import time
import numpy as np
import serial
from toon.input.base_input import BaseInput, DummyTime


class BlamBirds(BaseInput):
    """Minimalistic Flock of Birds implementation.

    This uses the settings recommended by Ascension to achieve "snappy" settings.
    """
    def __init__(self, clock_source=DummyTime(),
                 multiprocess=False,
                 buffer_rows=10,
                 ports=None,
                 master=None,
                 data_mode='position'):
        """

        Kwargs:
            clock_source: Class that provides a `getTime` method. Default object calls :fun:`time.time()`.
            multiprocess (bool): Whether multiprocessing is enabled or not.
            buffer_rows (int): Sets the number of rows in the shared array.
            ports (list of strings): List of ports with birds attached, e.g. ['COM4', 'COM5']
            master (string): The master bird.
            data_mode (string): Data format returned by the flock of birds. Currently, only
                                'position' is allowed.

        Notes:
            The data returned represents [x, y, z] elements per bird.

        Examples:

            >>> birds = BlamBirds(ports=['COM5', 'COM6', 'COM7'], master='COM5')
        """

        if master not in ports:
            raise ValueError('The master must be named amongst the ports.')
        if data_mode not in ['position']:
            raise ValueError('Invalid or unimplemented data mode.')
        self._ncol = 3 * len(ports)  # assumes only position data
        super(BlamBirds, self).__init__(clock_source, multiprocess, (buffer_rows, self._ncol))
        self._birds = None
        self.ports = ports
        self.master = master
        self._master_index = ports.index(master)
        self.data_mode = data_mode
        self._bird_data = np.full(self._ncol, np.nan)  # fill with bird data later
        self._reindex = (np.array([range(len(ports))]).reshape((len(ports), 1)) * 3 + np.tile([1, 2, 0], (len(ports), 1))).reshape(self._ncol)

    def _init_device(self):
        """FOB-specific initialization.

        """
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
        time.sleep(1.5)
        self._birds[self._master_index].write(('P' + chr(0x32) + chr(len(self.ports))).encode('UTF-8'))
        time.sleep(1.5)
        # set sampling frequency (130)
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

    def _read(self):
        """FOB-specific read function."""
        timestamp = self.time.getTime()
        _datalist = list()
        for bird in self._birds:
            _datalist.append(bird.read(6))  # assumes position data
        # don't convert if data not there
        if not any(b'' == s for s in _datalist):
            _datalist = [self.decode(msg) for msg in _datalist]
            data = np.array(_datalist).reshape((self._ncol,))  # assumes position data from two birds
            data[:] = data[self._reindex[:self._ncol]]  # reorder
            # rotate
            tmp_x = data[::3]
            tmp_y = data[1::3]
            data[::3] = tmp_x * np.cos(-0.01938) - tmp_y * np.sin(-0.01938)
            data[1::3] = tmp_x * np.sin(-0.01938) + tmp_y * np.cos(-0.01938)

            # translate
            # first number is shift calculated by Aaron
            # second number makes the center of the screen (0, 0)
            data[::3] += 61.35 - 60.5
            data[1::3] += 17.69 - 34.0
            return data, timestamp
        return None, None

    def _stop_device(self):
        """Tell the birds to stop streaming"""
        for bird in self._birds:
            bird.write(b'?')  # stop stream

    def _close_device(self):
        """Send the sleep command."""
        for bird in self._birds:
            bird.write(b'G') # sleep (light should go off)
        for bird in self._birds:
            bird.close()  # close serial communication

    def decode(self, msg, n_words=3):
        """Convert from word to data."""
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
