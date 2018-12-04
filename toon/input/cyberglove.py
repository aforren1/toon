import struct
import serial
from toon.input.device import BaseDevice, Obs


class Cyberglove(BaseDevice):
    sampling_frequency = 100

    class Pos(Obs):
        shape = (10,)
        ctype = int

    def __init__(self, port, **kwargs):
        super(Cyberglove, self).__init__(**kwargs)
        self.port = port  # TODO: auto-detect using serial.tools.list_ports
        self.dev = None

    def __enter__(self):
        self.dev = serial.Serial(self.port, 115200, timeout=0.05)
        self.dev.reset_input_buffer()
        self.dev.write(b'S')
        return self

    def read(self):
        data = glove.read(20)
        time = self.clock()
        if data:
            data = struct.unpack('<' + 'H' * 10, data)
            return self.Returns(self.Pos(time, data))

    def __exit__(self, *args):
        self.dev.write(b'\x03')
        self.dev.close()
