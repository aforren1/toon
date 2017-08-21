import serial
from input_base import InputBase
from multiprocessing import Process, Manager

class FlockOfBirds(InputBase):
    """Flock of birds class. Defined only for a single bird"""

    def __init__(self, port, clock_source=None):
        super(FlockOfBirds, self).__init__(clock_source)
        self.port = port
        self.serial = serial.Serial(self.port, baudrate=115200)
        self.process = None

    def start(self):
        self.process = Process

    def read(self):
        return

    def write(self, data):
        return

"""Write to log file, """