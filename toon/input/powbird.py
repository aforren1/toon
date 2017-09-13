import time
import struct
import numpy as np
import serial


# Ascension settings:
# stream mode (done)
# sudden output change lock = 0 (done)
# dc filter ON, AC narrow notch filter ON, AC wide notch OFF (done)
# Vm table = 2, 2, 2, 10, 10, 40, 200 (done)
class FobOut(object):
    def __init__(self, char=None, size=None, scales=None):
        self.char = char
        self.size = size
        self.scales = scales


class OneBird(object):
    def __init__(self, port=None, data_mode='position', master=False, num_birds=None):
        self.serial = None
        self.port = port
        self.data_mode = data_mode
        self.master = master
        self.num_birds = num_birds
        pos_scale = 36 * 2.54
        self.output_types = dict(angles=FobOut(b'W', 6, [180] * 3),
                                 position=FobOut(b'V', 6, [pos_scale] * 3),
                                 position_angles=FobOut(b'Y', 12, [pos_scale] * 3 + [180] * 3),
                                 matrix=FobOut(b'X', 18, [1] * 9),
                                 position_matrix=FobOut(b'Z', 24, [pos_scale] * 3 + [1] * 9),
                                 quaternion=FobOut(b'\\', 8, [1] * 4),
                                 position_quaternion=FobOut(b']', 14, [pos_scale] * 3 + [1] * 4))

    def open(self):
        self.serial = serial.Serial(port=self.port,
                                    baudrate=115200,
                                    bytesize=serial.EIGHTBITS,
                                    xonxoff=0,
                                    rtscts=0,
                                    timeout=1)
        self.serial.setRTS(0)
        # set data output type
        self.serial.write(self.output_types[self.data_mode].char)
        if self.master:
            # fbb_auto_config
            time.sleep(1.0)
            self.serial.write(('P' + chr(0x32) + chr(self.num_birds)).encode('UTF-8'))
            time.sleep(1.0)
        # change bird measurement rate to 138 hz (not sure about endianness...)
        self.serial.write(b'P' + b'\x07' + struct.pack('>H', int(138 * 256)))
        # change Vm table to Ascension's "snappy" settings
        self.serial.write(b'P' + b'C' + struct.pack('>HHHHHHH', *[2, 2, 2, 10, 10, 40, 200]))
        # Turn off Sudden Output Change Lock (should already be off...)
        self.serial.write(b'P' + b'E' + b'\x00')
        # first 5 bits are meaningless, B2 is 0 (AC narrow ON), B1 is 1 (AC wide OFF), B0 is 0 (DC ON)
        self.serial.write(('P' + '\x04' + '\x00' + '\x02').encode('UTF-8'))

    def decode(self, msg, n_words=None):
        if n_words is None:
            n_words = self.output_types[self.data_mode].size / 2
        return [self._decode_words(msg, i) for i in range(int(n_words))]

    def _decode_word(self, msg):
        lsb = ord(msg[0]) & 0x7f
        msb = ord(msg[1])
        v = (msb << 9) | (lsb << 2)
        if v < 0x8000:
            return v
        return v - 0x10000

    def _decode_words(self, s, i):
        v = self._decode_word(s[2 * i:2 * i + 2])
        v *= self.output_types[self.data_mode].scales[i]
        return v / 32768.0  # v to centimeters (???)

    def start(self):
        self.serial.write(b'F')  # run
        self.serial.write(b'@')  # stream

    def read(self):
        data = self.serial.read(self.output_types[self.data_mode].size)
        return self.decode(data)

    def clear(self):
        while True:
            s = self.serial.read(1)
            if s == '':
                break

    def stop(self):
        self.serial.write(b'?')  # stop stream

    def close(self):
        self.stop()
        self.serial.write(b'G')  # sleep
        self.serial.close()


class FlockOfBirds(object):
    """Manages individual birds (we never use group mode)"""

    def __init__(self, ports=None, data_mode='position', master=None):

        if master not in ports:
            raise ValueError('The master must be named among the ports.')

        if data_mode not in ['angles', 'position', 'position_angles',
                             'matrix', 'position_matrix', 'quaternion',
                             'position_quaternion']:
            raise ValueError('Invalid data mode.')

        self.ports = ports
        self.data_mode = data_mode
        self.master = master
        self.birds = [OneBird(port=x, data_mode=data_mode,
                              master=master == x,
                              num_birds=len(ports))
                      for x in ports]

    def open(self):
        # start the master first (which sends the auto config)
        master_index = self.ports.index(self.master)
        self.birds[master_index].open()

        # remove master from consideration, open the slaves
        for ii in range(len(self.ports)):
            if ii == master_index:
                continue
            self.birds[ii].open()

    def start(self):
        for bird in self.birds:
            bird.start()

    def read(self):
        """Temporary, for the sake of figuring out whether this works..."""
        return [bird.read() for bird in self.birds]

    def stop(self):
        for bird in self.birds:
            bird.stop()

    def close(self):
        for bird in self.birds:
            bird.close()

    def clear(self):
        for bird in self.birds:
            bird.clear()
