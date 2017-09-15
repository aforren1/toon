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
    def __init__(self, char=None, sizes=None, scales=None,
                 numpy_fun=None, reshape_fun=None, correct_fun=None):
        self.char = char
        self.sizes = sizes
        self.scales = scales
        self.numpy_fun = numpy_fun
        self.reshape_fun = reshape_fun
        self.correct_fun = correct_fun


def do_nothing(*args):
    return args[0]


def correct_pos(vals):
    tmp_x = vals[0]
    tmp_y = vals[1]
    vals[0] = tmp_x * np.cos(-0.01938) - tmp_y * np.sin(-0.01938)
    vals[1] = tmp_x * np.sin(-0.01938) + tmp_y * np.cos(-0.01938)
    vals[0] += 61.35
    vals[1] += 17.69
    return vals


class OneBird(object):
    def __init__(self, port=None, data_mode='position', master=False, num_birds=None, timer=None):
        self.serial = None
        self.port = port
        self.data_mode = data_mode
        self.master = master
        self.num_birds = num_birds
        self.timer = timer
        self.time0 = self.timer()

        self._x_offset = 61.35  # centimeters
        self._y_offset = 17.69  # centimeters
        self._xy_rotation = -0.01938  # radians
        pos_scale = 36 * 2.54  # convert to centimeters

        self.output_types = dict(angles=FobOut(b'W', [6], [180] * 3, np.array, do_nothing, do_nothing),
                                 position=FobOut(b'V', [6], [pos_scale] * 3, np.array, do_nothing, correct_pos),
                                 position_angles=FobOut(b'Y', [6, 6],
                                                        [pos_scale] * 3 + [180] * 3,
                                                        np.array,
                                                        [do_nothing, do_nothing],
                                                        [correct_pos, do_nothing]),
                                 matrix=FobOut(b'X', [18], [1] * 9, np.array, np.reshape, do_nothing),
                                 position_matrix=FobOut(b'Z', [6, 18],
                                                        [pos_scale] * 3 + [1] * 9,
                                                        np.array,
                                                        [do_nothing, np.reshape],
                                                        [correct_pos, do_nothing]),
                                 quaternion=FobOut(b'\\', [8], [1] * 4, np.array, do_nothing, do_nothing),
                                 position_quaternion=FobOut(b']', [6, 8],
                                                            [pos_scale] * 3 + [1] * 4,
                                                            np.array,
                                                            [do_nothing, do_nothing],
                                                            [correct_pos, do_nothing])
                                 )

        self.serial = serial.Serial(port=self.port,
                                    baudrate=115200,
                                    bytesize=serial.EIGHTBITS,
                                    xonxoff=0,
                                    rtscts=0,
                                    timeout=0.01)  # play with timeouts, don't want to sit around for long...
        self.serial.setRTS(0)

    def open(self):
        if self.master:
            # fbb_auto_config
            time.sleep(1.0)
            self.serial.write(('P' + chr(0x32) + chr(self.num_birds)).encode('UTF-8'))
            time.sleep(1.0)
            # change bird measurement rate to 130 hz (not sure about endianness...)
            self.serial.write(b'P' + b'\x07' + struct.pack('<H', int(130 * 256)))

        # set data output type
        self.serial.write(self.output_types[self.data_mode].char)
        # change Vm table to Ascension's "snappy" settings
        self.serial.write(b'P' + b'\x0C' + struct.pack('<HHHHHHH', *[2, 2, 2, 10, 10, 40, 200]))
        # first 5 bits are meaningless, B2 is 0 (AC narrow ON), B1 is 1 (AC wide OFF), B0 is 0 (DC ON)
        self.serial.write(b'P' + b'\x04' + b'\x02' + b'\x00')

    def decode(self, msg, n_words=None):
        """ Words to floats"""
        if n_words is None:
            n_words = self.output_types[self.data_mode].size / 2
        return [self._decode_words(msg, i) for i in range(int(n_words))]

    def _decode_word(self, msg):
        lsb = msg[0] & 0x7f
        msb = msg[1]
        v = (msb << 9) | (lsb << 2)
        if v < 0x8000:
            return v
        return v - 0x10000

    def _decode_words(self, s, i):
        v = self._decode_word(s[2 * i:2 * i + 2])
        v *= self.output_types[self.data_mode].scales[i]
        return v / 32768.0  # v to centimeters

    def start(self):
        self.serial.write(b'@')  # stream

    def read(self):
        """
        Steps:
        1. read expected data size
        2. convert words to floats
        3. Convert to numpy array
        4. If multiple data types, split apart
        5. Apply reshape (for matrices)
        6. Apply corrections (for position)
        7. Return None if no data
        """
        tmp = self.output_types[self.data_mode]
        data_size = sum(tmp.sizes)
        time = self.timer() - self.time0
        data = self.serial.read(data_size)
        if data is not b'':
            if len(tmp.sizes) > 1:
                data1 = self.decode(data[:(tmp.sizes[0]+1)], n_words=int(tmp.sizes[0]/2))
                data2 = self.decode(data[(tmp.sizes[0]+1):], n_words=int(tmp.sizes[1]/2))
                data1 = tmp.numpy_fun(data1)
                data2 = tmp.numpy_fun(data2)
                data1 = tmp.correct_fun(tmp.reshape_fun(data1))
                data2 = tmp.correct_fun(tmp.reshape_fun(data2))
                return time, data1, data2  # multiple measurements (e.g. position_angle)
            else:
                data = self.decode(data, n_words=int(tmp.sizes[0]/2))
                data = tmp.numpy_fun(data)
                return time, tmp.correct_fun(tmp.reshape_fun(data))  # single type of measurement
        return None  # return nothing if empty string retrieved

    def clear(self):
        while True:
            s = self.serial.read(1)
            if s is b'':
                break

    def stop(self):
        self.serial.write(b'?')  # stop stream

    def close(self):
        self.stop()
        if self.master:
            self.serial.write(b'G')  # sleep
        self.serial.close()


class FlockOfBirds(object):
    """Manages individual birds (we never use group mode)

    Example:
    fob = FlockOfBirds(ports=['/dev/ttyUSB0', '/dev/ttyUSB2'],
                       master = '/dev/ttyUSB0')
    fob.open()
    fob.start()
    # ...
    fob.close()
    """

    def __init__(self, ports=None, data_mode='position', master=None, timer=time.time):

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
                              num_birds=len(ports),
                              timer=timer)
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
        results = [bird.read() for bird in self.birds]
        if any(res is None for res in results):
            return None
        return results

    def stop(self):
        for bird in self.birds:
            bird.stop()

    def close(self):
        for bird in self.birds:
            bird.close()

    def clear(self):
        for bird in self.birds:
            bird.clear()
