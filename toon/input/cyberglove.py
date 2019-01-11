import struct
import serial
import numpy as np
from time import sleep
from toon.input.device import BaseDevice, Obs

# thanks to ROS http://docs.ros.org/fuerte/api/cyberglove/html/serial__glove_8hpp.html
# for commands


class Cyberglove(BaseDevice):
    sampling_frequency = 150

    class Pos(Obs):
        # TODO: split into fingers/joints?
        shape = (18,)
        ctype = float

    def __init__(self, port, **kwargs):
        super(Cyberglove, self).__init__(**kwargs)
        self.port = port  # TODO: auto-detect using serial.tools.list_ports
        self.dev = None

    def __enter__(self):
        self.dev = serial.Serial(self.port, 115200, timeout=0.02)
        self.dev.reset_input_buffer()
        sleep(0.1)
        # test whether the device is connected/on
        self.dev.write(b'l ?\r')
        # should echo back & give result
        if not self.dev.read():
            raise ValueError('Make sure the device is switched on.')
        self.dev.write(b'f 0\r')  # stop filtering
        self.dev.write(b't 1152 1\r')  # 100 Hz
        self.dev.write(b'u 0\r')  # don't transmit status
        self.dev.write(b'l 1\r')  # light on
        sleep(0.1)
        self.dev.reset_input_buffer()
        self.dev.write(b'S')  # start streaming
        self.dev.flush()
        # not sure how to get rid of the rest of the garbage,
        # so spin until we find the first b'S'
        for i in range(40):
            tmp = self.dev.read()
            if tmp == b'S':
                self.dev.read(19)  # read the rest of the line
                break
        if i >= 39:
            raise ValueError('Did not find the start byte.')
        return self

    def read(self):
        # one byte (S)
        val = self.dev.read(1)
        time = self.clock()
        if val:
            data = self.dev.read(19)  # read remaining bytes ('<data> \x00')
            data = struct.unpack('<' + 'B' * 18, data[:-1])
            data = [(d - 1.0)/254.0 for d in data]
            return self.Returns(self.Pos(time, data))

    def __exit__(self, *args):
        self.dev.write(b'\x03')  # stop streaming
        self.dev.write(b'l 0\r')  # light off
        sleep(0.1)
        self.dev.reset_input_buffer()
        self.dev.reset_output_buffer()
        self.dev.close()
